"""Exercise the wire client without sending anything to a real player."""

import asyncio
import json
from collections import deque
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import web

from custom_components.ottplay import api
from custom_components.ottplay.api import (
    AuthError,
    CannotConnect,
    CommandRejected,
    CommandUnsupported,
    OttplayClient,
    PlayerUnavailable,
    ProtocolError,
    RateLimited,
    normalize_url,
)

TOKEN = "private-credential-" + "x" * 24
RID = "a" * 32


class Response:
    def __init__(self, status, payload, headers=None):
        self.status = status
        self.payload = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.headers = headers or {}
        self.content = self

    async def iter_chunked(self, size):
        for offset in range(0, len(self.payload), size):
            yield self.payload[offset : offset + size]

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        pass


class Session:
    def __init__(self, *responses):
        self.responses = deque(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.popleft()
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture(autouse=True)
def fast_requests(monkeypatch):
    monkeypatch.setattr(api, "REQUEST_INTERVAL", 0)
    monkeypatch.setattr(api, "POLL_INTERVAL", 0)


def client(*responses):
    session = Session(*responses)
    return OttplayClient(session, "https://controller.example/control/", TOKEN), session


def receipt(data, *, status="ok", request_id=RID):
    return Response(200, {"id": request_id, "status": status, "data": data})


@pytest.mark.parametrize(
    "value",
    [
        "file:///etc/passwd",
        "http://name:password@localhost",
        "https://host/?token=secret",
        "https://host/#secret",
        "https://host/%2e%2e/other",
        "https://host/../other",
        "https://host//other",
        "https://ho st/",
        "https://host\\@else/",
        "https://host:bad/",
    ],
)
def test_unsafe_base_url_rejected(value):
    with pytest.raises(ValueError, match="Invalid control server URL"):
        normalize_url(value)


def test_url_normalization_supports_private_base_path():
    assert (
        normalize_url("http://192.168.1.4:8081/ott-control/")
        == "http://192.168.1.4:8081/ott-control"
    )
    assert normalize_url("https://EXAMPLE.COM") == "https://example.com"


@pytest.mark.parametrize("token", ["short", "x" * 257, "x" * 32 + "\n", "x" * 32 + ":"])
def test_bad_credential_rejected(token):
    with pytest.raises(ValueError):
        OttplayClient(Session(), "https://host", token)


async def test_registry_preserves_offline_devices_and_aware_activity():
    value, session = client(
        Response(
            200,
            {
                "devices": [
                    {
                        "id": "living:room",
                        "pending": 1,
                        "last_seen": "2026-10-19T12:00:00.123456789Z",
                    },
                    {"id": "offline", "pending": 0, "last_seen": None},
                ]
            },
        )
    )
    devices = await value.async_devices()
    assert devices[0].id == "living:room"
    assert devices[0].last_seen.tzinfo == timezone.utc
    assert devices[1].last_seen is None
    method, url, options = session.calls[0]
    assert (method, url) == ("GET", "https://controller.example/control/api/devices")
    assert options["allow_redirects"] is False
    assert options["headers"]["Authorization"] == "Bearer " + TOKEN
    assert options["headers"]["User-Agent"].startswith("ha-ottplay/")


@pytest.mark.parametrize(
    "rows",
    [
        [{"id": "same"}, {"id": "same"}],
        [{"id": "bad/id"}],
        [{"id": "d1", "pending": True}],
        [{"id": "d1", "last_seen": "2026-10-19T12:00:00"}],
        [{"id": "d1", "last_seen": 42}],
        [None],
        [{}],
        [{"id": str(n)} for n in range(65)],
    ],
)
async def test_registry_rejects_unsafe_metadata(rows):
    value, _ = client(Response(200, {"devices": rows}))
    with pytest.raises(ProtocolError):
        await value.async_devices()


async def test_command_polls_same_receipt_and_submits_once():
    value, session = client(
        Response(202, {"id": RID}),
        Response(202, {"status": "pending"}),
        aiohttp.ClientConnectionError("contains-secret"),
        receipt({"dispatched": True}),
    )
    assert await value.async_call("d1", "playback", {"operation": "next_channel"}) == {
        "dispatched": True
    }
    assert [call[0] for call in session.calls] == ["POST", "GET", "GET", "GET"]
    assert all(call[2]["params"]["id"] == RID for call in session.calls[1:])


async def test_lost_submit_response_is_never_retried_or_exposed():
    value, session = client(aiohttp.ClientConnectionError(TOKEN))
    with pytest.raises(CannotConnect) as caught:
        await value.async_call("d1", "playback", {"operation": "next_channel"})
    assert TOKEN not in str(caught.value)
    assert len(session.calls) == 1


@pytest.mark.parametrize(
    "status,error",
    [
        (401, AuthError),
        (403, AuthError),
        (302, ProtocolError),
        (500, CannotConnect),
        (404, ProtocolError),
    ],
)
async def test_http_errors_redact_response_and_do_not_redirect(status, error):
    value, session = client(
        Response(status, {"secret": TOKEN}, {"Location": "https://other.example"})
    )
    with pytest.raises(error) as caught:
        await value.async_devices()
    assert TOKEN not in str(caught.value)
    assert len(session.calls) == 1


async def test_server_backoff_sets_shared_deadline_without_replay():
    value, session = client(Response(429, {}, {"Retry-After": "60"}))
    before = api.time.monotonic()
    with pytest.raises(RateLimited):
        await value.async_call("d1", "play", {"query": "1"})
    assert value._next_request >= before + 59
    assert len(session.calls) == 1
    with pytest.raises(RateLimited, match="cooldown"):
        await value.async_devices()
    assert len(session.calls) == 1


async def test_cooldown_is_rechecked_after_waiting_for_a_slot(monkeypatch):
    value, session = client()
    value._next_request = api.time.monotonic() + 1

    async def backoff_arrives(_delay):
        value._cooldown_until = api.time.monotonic() + 60

    monkeypatch.setattr(api.asyncio, "sleep", backoff_arrives)
    with pytest.raises(RateLimited, match="cooldown"):
        await value.async_devices()
    assert not session.calls


async def test_receipt_polling_does_not_retry_after_rate_limit():
    value, session = client(Response(202, {"id": RID}), Response(429, {}))
    with pytest.raises(RateLimited):
        await value.async_call("d1", "play", {"query": "1"})
    assert len(session.calls) == 2


@pytest.mark.parametrize(
    "payload",
    [
        b'{"devices":[],"devices":[]}',
        b'{"value":NaN}',
        b'{"value":1e999}',
        b"[]",
        b"not-json",
    ],
)
async def test_invalid_json_is_rejected(payload):
    value, _ = client(Response(200, payload))
    with pytest.raises(ProtocolError):
        await value.async_devices()


async def test_response_limit_is_streamed(monkeypatch):
    monkeypatch.setattr(api, "MAX_RESPONSE_BYTES", 8)
    value, _ = client(Response(200, {"devices": []}))
    with pytest.raises(ProtocolError, match="size limit"):
        await value.async_devices()


@pytest.mark.parametrize(
    "outcome,error", [("rejected", CommandRejected), ("unsupported", CommandUnsupported)]
)
async def test_player_negative_receipts_are_not_reported_as_success(outcome, error):
    value, _ = client(Response(202, {"id": RID}), receipt({"error": TOKEN}, status=outcome))
    with pytest.raises(error) as caught:
        await value.async_call("d1", "play", {"query": "1"})
    assert TOKEN not in str(caught.value)


async def test_mismatched_receipt_fails_closed():
    value, _ = client(Response(202, {"id": RID}), receipt({}, request_id="b" * 32))
    with pytest.raises(ProtocolError, match="mismatched"):
        await value.async_call("d1", "status", {})


async def test_expired_receipt_is_not_treated_as_unsubmitted():
    value, session = client(Response(202, {"id": RID}), Response(404, {}))
    with pytest.raises(PlayerUnavailable, match="expired"):
        await value.async_call("d1", "play", {"query": "1"})
    assert [item[0] for item in session.calls] == ["POST", "GET"]


async def test_pending_deadline_does_not_repeat_mutation(monkeypatch):
    monkeypatch.setattr(api, "REQUEST_TIMEOUT", 0.005)
    value, _ = client()
    value._request = AsyncMock(
        side_effect=lambda method, *_args, **_kwargs: (
            (202, {"id": RID}) if method == "POST" else (202, {"status": "pending"})
        )
    )
    with pytest.raises(PlayerUnavailable, match="not replayed"):
        await value.async_call("d1", "play", {"query": "1"})
    assert sum(call.args[0] == "POST" for call in value._request.call_args_list) == 1


async def test_cancellation_is_preserved():
    value, _ = client()
    value._request = AsyncMock(side_effect=asyncio.CancelledError)
    with pytest.raises(asyncio.CancelledError):
        await value.async_call("d1", "status", {})


async def test_offline_validation_checks_acceptance_without_waiting():
    value, session = client(Response(202, {"id": RID}))
    await value.async_validate("d1")
    assert len(session.calls) == 1
    assert session.calls[0][2]["json"] == {"action": "status", "params": {}}


@pytest.mark.parametrize("method", ["async_validate", "async_call"])
async def test_invalid_device_id_cannot_issue_a_request(method):
    value, session = client()
    with pytest.raises(ValueError):
        await getattr(value, method)(
            "d1&other=target", *(["status", {}] if method == "async_call" else [])
        )
    assert not session.calls


async def test_offline_validation_requires_valid_accepted_id():
    value, _ = client(Response(202, {"id": "bad"}))
    with pytest.raises(ProtocolError):
        await value.async_validate("d1")


def snapshots():
    status = {
        "player": {"runtime": "page-123", "version": "1.1.56", "platform": "browser"},
        "volume": 30,
        "ready": True,
    }
    capabilities = {
        "player": dict(status["player"]),
        "playback": ["next_channel"],
        "input": ["up"],
        "lifecycle": [],
        "inspect": {"version": 1, "sections": ["doctor"]},
    }
    doctor = {
        "version": 1,
        "runtime": "page-123",
        "consistent": True,
        "media": {
            "kind": "live",
            "phase": "playing",
            "lanes": [{"lane": "main", "phase": "playing", "position": 15, "duration": None}],
        },
    }
    envelope = {"version": 1, "runtime": "page-123", "section": "doctor", "data": doctor}
    return status, capabilities, envelope


async def test_snapshot_is_bound_to_one_runtime_and_preserves_observations():
    value, _ = client()
    data = snapshots()
    value.async_call = AsyncMock(side_effect=data)
    snapshot = await value.async_snapshot("d1")
    assert snapshot.status["volume"] == 30
    assert snapshot.doctor["media"]["phase"] == "playing"
    assert isinstance(snapshot.observed_at, datetime)
    assert snapshot.observed_at.tzinfo == timezone.utc
    assert value.async_call.call_args_list[2].args == (
        "d1",
        "inspect",
        {"version": 1, "runtime": "page-123", "section": "doctor"},
    )


async def test_runtime_change_discards_mixed_snapshot():
    value, _ = client()
    status, capabilities, _ = snapshots()
    capabilities["player"]["runtime"] = "page-new"
    value.async_call = AsyncMock(side_effect=[status, capabilities])
    with pytest.raises(PlayerUnavailable, match="runtime changed"):
        await value.async_snapshot("d1")


async def test_older_player_retains_unknown_media_state():
    value, _ = client()
    status, capabilities, _ = snapshots()
    capabilities.pop("inspect")
    value.async_call = AsyncMock(side_effect=[status, capabilities])
    assert (await value.async_snapshot("d1")).doctor is None
    assert value.async_call.await_count == 2


async def test_optional_inspection_rejection_is_unknown_not_playing():
    value, _ = client()
    status, capabilities, _ = snapshots()
    value.async_call = AsyncMock(side_effect=[status, capabilities, CommandRejected()])
    assert (await value.async_snapshot("d1")).doctor is None


async def test_unsupported_status_marks_player_unavailable():
    value, _ = client()
    value.async_call = AsyncMock(side_effect=CommandUnsupported())
    with pytest.raises(PlayerUnavailable):
        await value.async_snapshot("d1")


@pytest.mark.parametrize(
    "change",
    [
        lambda status, caps: status.update(player=None),
        lambda status, caps: status["player"].update(runtime="https://elsewhere"),
        lambda status, caps: status.update(volume=True),
        lambda status, caps: status.update(volume=101),
        lambda status, caps: caps.update(playback=[{}]),
    ],
)
async def test_invalid_status_or_capabilities_fail_closed(change):
    value, _ = client()
    status, caps, _ = snapshots()
    change(status, caps)
    value.async_call = AsyncMock(side_effect=[status, caps])
    with pytest.raises(ProtocolError):
        await value.async_snapshot("d1")


@pytest.mark.parametrize(
    "change",
    [
        lambda value: value.update(runtime="other-page"),
        lambda value: value["data"].update(runtime="other-page"),
        lambda value: value["data"]["media"].update(lanes=[None]),
        lambda value: value["data"]["media"]["lanes"][0].update(position=float("inf")),
        lambda value: value["data"]["media"].update(phase="invented-state"),
    ],
)
async def test_malformed_observations_fail_closed(change):
    value, _ = client()
    status, capabilities, envelope = snapshots()
    change(envelope)
    value.async_call = AsyncMock(side_effect=[status, capabilities, envelope])
    with pytest.raises(ProtocolError):
        await value.async_snapshot("d1")


async def test_real_http_wire_and_redirect_boundary():
    """Exercise aiohttp itself, so mocks cannot hide query/header mistakes."""
    calls = []
    redirected = []

    async def endpoint(request):
        assert request.headers["Authorization"] == "Bearer " + TOKEN
        assert request.headers["User-Agent"].startswith("ha-ottplay/")
        calls.append((request.method, dict(request.query)))
        if request.method == "POST":
            assert dict(request.query) == {"device_id": "room:1"}
            assert await request.json() == {
                "action": "playback",
                "params": {"operation": "next_channel"},
            }
            return web.json_response({"id": RID}, status=202)
        assert dict(request.query) == {"device_id": "room:1", "id": RID}
        return web.json_response({"id": RID, "status": "ok", "data": {"dispatched": True}})

    async def redirect(_request):
        raise web.HTTPFound("/private-target")

    async def target(request):
        redirected.append(dict(request.headers))
        return web.json_response({"devices": []})

    app = web.Application()
    app.router.add_route("*", "/control/api/requests", endpoint)
    app.router.add_get("/control/api/devices", redirect)
    app.router.add_get("/private-target", target)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        port = runner.addresses[0][1]
        async with aiohttp.ClientSession() as session:
            value = OttplayClient(session, f"http://127.0.0.1:{port}/control", TOKEN)
            assert await value.async_call("room:1", "playback", {"operation": "next_channel"}) == {
                "dispatched": True
            }
            with pytest.raises(ProtocolError):
                await value.async_devices()
        assert calls == [
            ("POST", {"device_id": "room:1"}),
            ("GET", {"device_id": "room:1", "id": RID}),
        ]
        assert not redirected
    finally:
        await runner.cleanup()

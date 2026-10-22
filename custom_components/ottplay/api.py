"""Bounded, asynchronous client for the OTTPlay control server's request API.

An RPC is submitted exactly once. Polling its receipt is safe to retry; submitting
another RPC after a timeout is not, even when the first response was lost.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import DEVICE_ID_PATTERN, MAX_DEVICES, REQUEST_TIMEOUT
from .protocol import normalize_url
from .protocol import valid_number as _number

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
REQUEST_INTERVAL = 0.5  # At most 120 requests/minute, below the server's 240.
POLL_INTERVAL = 1.0
_REQUEST_ID = re.compile(r"[0-9a-f]{32}")
_RUNTIME = re.compile(r"[A-Za-z0-9_.-]{1,96}")


class OttplayError(Exception):
    """Base error with a safe message that never includes response bodies."""


class AuthError(OttplayError):
    """The credential is invalid or lacks the requested scope."""


class CannotConnect(OttplayError):
    """The control server could not be reached."""


class RateLimited(CannotConnect):
    """The server requested a cooldown; no command was replayed."""


class ProtocolError(OttplayError):
    """The server returned a malformed or mismatched response."""


class PlayerUnavailable(OttplayError):
    """A player did not supply a usable receipt before the deadline."""


class CommandRejected(OttplayError):
    """The player rejected a command, including local policy restrictions."""


class CommandUnsupported(OttplayError):
    """The player does not support the requested operation."""


@dataclass(frozen=True)
class Device:
    """Registered player metadata, not evidence of successful playback."""

    id: str
    last_seen: datetime | None
    pending: int = 0


@dataclass(frozen=True)
class PlayerSnapshot:
    """Observations of one page runtime, with unavailable values left unknown."""

    status: dict[str, Any]
    capabilities: dict[str, Any]
    doctor: dict[str, Any] | None
    observed_at: datetime


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(_value: str) -> None:
    raise ValueError("Nonfinite JSON number")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Nonfinite JSON number")
    return number


class OttplayClient:
    """Share a Home Assistant HTTP session without changing its global defaults."""

    def __init__(self, session: ClientSession, url: str, token: str) -> None:
        self.url = normalize_url(url)
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{32,256}", token):
            raise ValueError("Invalid control server token")
        self._session = session
        self._token = token
        self._rate_lock = asyncio.Lock()
        self._next_request = 0.0
        self._cooldown_until = 0.0

    async def _pace(self) -> None:
        async with self._rate_lock:
            if self._cooldown_until > time.monotonic():
                raise RateLimited("Control server rate limit cooldown is active")
            delay = self._next_request - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            # Another in-flight response may have extended the cooldown while
            # this request waited for its ordinary pacing slot.
            if self._cooldown_until > time.monotonic():
                raise RateLimited("Control server rate limit cooldown is active")
            self._next_request = time.monotonic() + REQUEST_INTERVAL

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        await self._pace()
        try:
            async with self._session.request(
                method,
                self.url + path,
                params=params,
                json=body,
                headers={
                    "Authorization": "Bearer " + self._token,
                    "User-Agent": "ha-ottplay/0.1.0",
                },
                allow_redirects=False,
                timeout=ClientTimeout(total=10),
            ) as response:
                status = response.status
                if status in (401, 403):
                    raise AuthError("Invalid credential or missing device/action scope")
                if status == 429:
                    retry = response.headers.get("Retry-After", "60")
                    delay = min(300, max(1, int(retry))) if retry.isdecimal() else 60
                    self._next_request = max(self._next_request, time.monotonic() + delay)
                    self._cooldown_until = self._next_request
                    raise RateLimited("Control server rate limit reached")
                if status == 404:
                    if method == "GET" and path == "/api/requests" and params and "id" in params:
                        raise PlayerUnavailable("The request receipt is missing or expired")
                    raise ProtocolError("Control server endpoint is unavailable")
                if status >= 500:
                    raise CannotConnect("Control server unavailable")
                if status not in (200, 202):
                    # In particular, never follow a redirect with a bearer credential.
                    raise ProtocolError("Unexpected control server HTTP response")
                raw = bytearray()
                async for chunk in response.content.iter_chunked(65536):
                    raw.extend(chunk)
                    if len(raw) > MAX_RESPONSE_BYTES:
                        raise ProtocolError("Control server response exceeds size limit")
                try:
                    value = json.loads(
                        raw,
                        object_pairs_hook=_object,
                        parse_constant=_nonfinite,
                        parse_float=_finite_float,
                    )
                except ValueError, RecursionError, UnicodeError:
                    raise ProtocolError("Control server returned invalid JSON") from None
                if not isinstance(value, dict):
                    raise ProtocolError("Control server returned a non-object response")
                return status, value
        except ClientError, OSError, TimeoutError:
            raise CannotConnect("Control server connection failed") from None

    async def async_devices(self) -> list[Device]:
        """Read the registry; existing servers require the administrator token."""
        status, payload = await self._request("GET", "/api/devices")
        rows = payload.get("devices")
        if status != 200 or not isinstance(rows, list) or len(rows) > MAX_DEVICES:
            raise ProtocolError("Invalid device registry")
        result: list[Device] = []
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ProtocolError("Invalid registered device")
            identifier, pending = row.get("id"), row.get("pending", 0)
            if (
                not isinstance(identifier, str)
                or not re.fullmatch(DEVICE_ID_PATTERN, identifier)
                or identifier in seen
                or type(pending) is not int
                or not 0 <= pending <= 50
            ):
                raise ProtocolError("Invalid registered device")
            seen.add(identifier)
            stamp = row.get("last_seen")
            last_seen = None
            if stamp is not None:
                try:
                    if not isinstance(stamp, str):
                        raise ValueError
                    last_seen = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                    if last_seen.tzinfo is None:
                        raise ValueError
                except ValueError:
                    raise ProtocolError("Invalid device activity timestamp") from None
            result.append(Device(identifier, last_seen, pending))
        return result

    async def async_validate(self, device_id: str) -> None:
        """Validate an explicit player's scope without waiting for it to be online."""
        if not re.fullmatch(DEVICE_ID_PATTERN, device_id):
            raise ValueError("Invalid device ID")
        status, queued = await self._request(
            "POST",
            "/api/requests",
            params={"device_id": device_id},
            body={"action": "status", "params": {}},
        )
        request_id = queued.get("id")
        if (
            status != 202
            or not isinstance(request_id, str)
            or not _REQUEST_ID.fullmatch(request_id)
        ):
            raise ProtocolError("Invalid request identifier")

    async def async_call(
        self, device_id: str, action: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit once, then poll only that receipt within a total deadline."""
        if not re.fullmatch(DEVICE_ID_PATTERN, device_id):
            raise ValueError("Invalid device ID")
        query = {"device_id": device_id}
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                status, queued = await self._request(
                    "POST", "/api/requests", params=query, body={"action": action, "params": params}
                )
                request_id = queued.get("id")
                if (
                    status != 202
                    or not isinstance(request_id, str)
                    or not _REQUEST_ID.fullmatch(request_id)
                ):
                    raise ProtocolError("Invalid request identifier; command was not replayed")
                query["id"] = request_id
                while True:
                    await asyncio.sleep(POLL_INTERVAL)
                    try:
                        status, receipt = await self._request("GET", "/api/requests", params=query)
                    except RateLimited:
                        raise
                    except CannotConnect:
                        # GET is side-effect free. Keep the original request ID.
                        continue
                    if status == 202:
                        if receipt.get("status") != "pending":
                            raise ProtocolError("Invalid pending receipt")
                        continue
                    outcome = receipt.get("status")
                    data = receipt.get("data")
                    if (
                        receipt.get("id") != request_id
                        or outcome not in ("ok", "rejected", "unsupported")
                        or not isinstance(data, dict)
                    ):
                        raise ProtocolError("Invalid or mismatched player receipt")
                    if outcome == "rejected":
                        raise CommandRejected("Player rejected the operation")
                    if outcome == "unsupported":
                        raise CommandUnsupported("Player does not support the operation")
                    return data
        except TimeoutError:
            raise PlayerUnavailable("Player response timed out; command was not replayed") from None

    async def async_snapshot(self, device_id: str) -> PlayerSnapshot:
        """Read status, dynamic capabilities and an optional bounded media sample."""
        try:
            status = await self.async_call(device_id, "status", {})
            capabilities = await self.async_call(device_id, "capabilities", {})
        except CommandRejected, CommandUnsupported:
            raise PlayerUnavailable("Player does not provide status/capabilities") from None
        player = status.get("player")
        cap_player = capabilities.get("player")
        if not isinstance(player, dict) or not isinstance(cap_player, dict):
            raise ProtocolError("Invalid player identity")
        runtime = player.get("runtime")
        if not isinstance(runtime, str) or not _RUNTIME.fullmatch(runtime):
            raise ProtocolError("Invalid player runtime")
        if cap_player.get("runtime") != runtime:
            raise PlayerUnavailable("Player runtime changed during collection")
        volume = status.get("volume")
        if volume is not None and not _number(volume, 0, 100):
            raise ProtocolError("Invalid player volume")
        for name in ("playback", "lifecycle", "input"):
            values = capabilities.get(name)
            if (
                not isinstance(values, list)
                or len(values) > 64
                or any(not isinstance(v, str) for v in values)
            ):
                raise ProtocolError("Invalid player capabilities")
        doctor = None
        inspect = capabilities.get("inspect")
        if (
            isinstance(inspect, dict)
            and inspect.get("version") == 1
            and isinstance(inspect.get("sections"), list)
            and "doctor" in inspect["sections"]
        ):
            try:
                envelope = await self.async_call(
                    device_id, "inspect", {"version": 1, "runtime": runtime, "section": "doctor"}
                )
                candidate = envelope.get("data")
                if (
                    envelope.get("version") != 1
                    or envelope.get("runtime") != runtime
                    or envelope.get("section") != "doctor"
                    or not isinstance(candidate, dict)
                    or candidate.get("runtime") != runtime
                    or candidate.get("version") != 1
                    or not isinstance(candidate.get("media"), dict)
                    or type(candidate.get("consistent")) is not bool
                ):
                    raise ProtocolError("Invalid or mismatched media snapshot")
                media = candidate["media"]
                phases = {
                    "idle",
                    "loading",
                    "playing",
                    "paused",
                    "stopped",
                    "ended",
                    "error",
                    "unknown",
                }
                if (
                    media.get("kind") not in ("live", "archive", "vod", "none", "unknown")
                    or media.get("phase") not in phases
                    or not isinstance(media.get("lanes"), list)
                    or len(media["lanes"]) > 2
                ):
                    raise ProtocolError("Invalid media observation")
                lanes = set()
                for lane in media["lanes"]:
                    if (
                        not isinstance(lane, dict)
                        or lane.get("lane") not in ("main", "pip")
                        or lane["lane"] in lanes
                        or lane.get("phase") not in phases
                        or any(
                            lane.get(key) is not None and not _number(lane[key])
                            for key in ("position", "duration")
                        )
                    ):
                        raise ProtocolError("Invalid media lane")
                    lanes.add(lane["lane"])
                doctor = candidate
            except CommandRejected, CommandUnsupported:
                # Older players may advertise an unavailable inspection producer.
                pass
        return PlayerSnapshot(status, capabilities, doctor, datetime.now(timezone.utc))

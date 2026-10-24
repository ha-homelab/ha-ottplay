"""Fleet fairness, offline handling, lifecycle and mutation boundaries."""

import asyncio
import time
from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from conftest import make_entry
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.ottplay.api import AuthError, CannotConnect, Device, PlayerUnavailable
from custom_components.ottplay.coordinator import OttplayCoordinator


async def command_observations_finished(coordinator):
    """Include a coalesced follow-up created when an older observation finishes."""
    while coordinator._command_refresh_tasks:
        await asyncio.gather(*coordinator._command_refresh_tasks.values())


async def test_offline_fleet_setup_immediate_then_fair(hass, entry, client):
    ids = [f"player-{i:02}" for i in range(24)]
    entry = make_entry(ids)
    client.async_snapshot.side_effect = PlayerUnavailable()
    coordinator = OttplayCoordinator(hass, entry, client)
    first = await coordinator._async_update_data()
    assert set(first) == set(ids) and all(value is None for value in first.values())
    client.async_snapshot.assert_not_awaited()
    coordinator.async_set_updated_data(first)
    for _ in range(6):
        coordinator.async_set_updated_data(await coordinator._async_update_data())
    assert sorted(call.args[0] for call in client.async_snapshot.await_args_list) == sorted(ids)
    await coordinator._async_update_data()
    assert client.async_snapshot.await_count == 24
    await coordinator.async_shutdown()


async def test_admin_discovery_includes_never_seen_without_polling(hass, entry, client):
    entry = make_entry([])
    client.async_devices.return_value = [
        Device("offline", None),
        Device("online", datetime.now(timezone.utc)),
    ]
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data(await coordinator._async_update_data())
    updated = await coordinator._async_update_data()
    assert updated["offline"] is None and updated["online"] is not None
    client.async_snapshot.assert_awaited_once_with("online")
    client.async_devices.return_value = []
    coordinator.async_set_updated_data(updated)
    assert await coordinator._async_update_data() == {"online": None, "offline": None}
    await coordinator.async_shutdown()


async def test_authentication_and_network_failure(hass, entry, client):
    coordinator = OttplayCoordinator(hass, entry, client)
    await coordinator._async_update_data()
    client.async_snapshot.side_effect = AuthError()
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()
    entry = make_entry([])
    coordinator = OttplayCoordinator(hass, entry, client)
    client.async_devices.side_effect = CannotConnect()
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    await coordinator.async_shutdown()


async def test_sequence_once_then_failed_observation_is_unavailable(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    client.async_snapshot.side_effect = PlayerUnavailable()
    await coordinator.async_commands(
        "test-player", [("input", {"key": "ok"}), ("input", {"key": "back"})]
    )
    assert client.async_call.await_count == 2
    assert coordinator.data["test-player"] is snapshot
    await command_observations_finished(coordinator)
    assert coordinator.data["test-player"] is None
    with pytest.raises(ServiceValidationError):
        await coordinator.async_command("test-player", "playback", {"operation": "pause"})
    coordinator.async_set_updated_data({"test-player": snapshot})
    client.async_call.side_effect = PlayerUnavailable()
    with pytest.raises(HomeAssistantError):
        await coordinator.async_command("test-player", "playback", {"operation": "pause"})
    assert coordinator.data["test-player"] is snapshot
    await command_observations_finished(coordinator)
    assert client.async_call.await_count == 3 and coordinator.data["test-player"] is None
    await hass.async_block_till_done()
    await coordinator.async_shutdown()


async def test_concurrent_commands_not_queued(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    coordinator.async_request_refresh = AsyncMock()
    entered, release = asyncio.Event(), asyncio.Event()

    async def call(*args):
        entered.set()
        await release.wait()

    client.async_call.side_effect = call
    task = asyncio.create_task(coordinator.async_command("test-player", "input", {"key": "ok"}))
    await entered.wait()
    with pytest.raises(ServiceValidationError):
        await coordinator.async_command("test-player", "input", {"key": "back"})
    release.set()
    await task
    assert client.async_call.await_count == 1
    await hass.async_block_till_done()
    await coordinator.async_shutdown()


@pytest.mark.parametrize("old_poll_fails", [False, True])
async def test_snapshot_cannot_restore_state_from_before_command(
    hass, entry, client, snapshot, old_poll_fails
):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot})
    entered, release = asyncio.Event(), asyncio.Event()
    fresh = replace(snapshot, status={**snapshot.status, "volume": 75})
    calls = 0

    async def slow_snapshot(device_id):
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            await release.wait()
            if old_poll_fails:
                raise PlayerUnavailable()
            return snapshot
        return fresh

    client.async_snapshot.side_effect = slow_snapshot
    refresh = asyncio.create_task(coordinator._async_update_data())
    await entered.wait()
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await command_observations_finished(coordinator)
    assert coordinator.data["test-player"] is fresh
    next_poll = coordinator._next_poll["test-player"]
    assert next_poll > time.monotonic()
    release.set()
    result = await refresh
    assert result["test-player"] is fresh
    assert coordinator._next_poll["test-player"] == next_poll
    await hass.async_block_till_done()
    await coordinator.async_shutdown()


async def test_cancelled_command_does_not_spawn_refresh(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    coordinator.async_request_refresh = AsyncMock()
    entered = asyncio.Event()

    async def pending(*args):
        entered.set()
        await asyncio.Event().wait()

    client.async_call.side_effect = pending
    command = asyncio.create_task(coordinator.async_command("test-player", "input", {"key": "ok"}))
    await entered.wait()
    command.cancel()
    with pytest.raises(asyncio.CancelledError):
        await command
    assert coordinator.data["test-player"] is snapshot
    assert not coordinator._command_refresh_tasks
    coordinator.async_request_refresh.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_volume_keeps_observed_state_until_targeted_refresh(hass, entry, client, snapshot):
    """Real HA eager task creation must not run the refresh under the command lock."""
    from homeassistant.components.media_player import MediaPlayerState

    from custom_components.ottplay.media_player import OttplayMediaPlayer

    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot})
    # No fleet refresh is requested or needed; even a future regular poll is irrelevant.
    coordinator._next_poll["test-player"] = time.monotonic() + 3600
    coordinator.async_request_refresh = AsyncMock()
    entity = OttplayMediaPlayer(coordinator, "test-player")
    entered, release = asyncio.Event(), asyncio.Event()
    observed = replace(snapshot, status={**snapshot.status, "volume": 70})

    async def read(device_id):
        assert not coordinator._command_locks[device_id].locked()
        entered.set()
        await release.wait()
        return observed

    client.async_snapshot.side_effect = read
    await entity.async_set_volume_level(0.75)
    client.async_call.assert_awaited_once_with(
        "test-player", "command", {"command": "set_volume", "volume": 75}
    )
    await entered.wait()
    assert entity.available and entity.state == MediaPlayerState.PLAYING
    assert entity.volume_level == 0.4  # No optimistic value from the command ACK.
    assert await coordinator._async_update_data() == {"test-player": snapshot}
    assert client.async_snapshot.await_count == 1  # No duplicate ordinary poll.
    release.set()
    await command_observations_finished(coordinator)
    assert entity.available and entity.state == MediaPlayerState.PLAYING
    assert entity.volume_level == 0.7  # Use the observation, not the requested 0.75.
    coordinator.async_request_refresh.assert_not_awaited()
    await coordinator.async_shutdown()


async def test_commands_coalesce_reads_and_drop_superseded_result(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    entered, release = asyncio.Event(), asyncio.Event()
    old_result = replace(snapshot, status={**snapshot.status, "volume": 50})
    final_result = replace(snapshot, status={**snapshot.status, "volume": 80})
    seen = []
    unsubscribe = coordinator.async_add_listener(
        lambda: seen.append(coordinator.data["test-player"])
    )

    async def read(device_id):
        if client.async_snapshot.await_count == 1:
            entered.set()
            await release.wait()
            return old_result
        return final_result

    client.async_snapshot.side_effect = read
    await coordinator.async_command(
        "test-player", "command", {"command": "set_volume", "volume": 50}
    )
    await entered.wait()
    for volume in (60, 70, 80):
        await coordinator.async_command(
            "test-player", "command", {"command": "set_volume", "volume": volume}
        )
    assert client.async_call.await_count == 4
    assert client.async_snapshot.await_count == 1
    release.set()
    await command_observations_finished(coordinator)
    assert client.async_snapshot.await_count == 2
    assert coordinator.data["test-player"] is final_result
    assert seen == [final_result]
    unsubscribe()
    await coordinator.async_shutdown()


async def test_targeted_timeout_bounds_retained_observation(
    hass, entry, client, snapshot, monkeypatch
):
    monkeypatch.setattr("custom_components.ottplay.coordinator.REQUEST_TIMEOUT", 0.001)
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})

    async def never_finishes(device_id):
        await asyncio.Event().wait()

    client.async_snapshot.side_effect = never_finishes
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await command_observations_finished(coordinator)
    assert coordinator.data["test-player"] is None
    assert client.async_call.await_count == client.async_snapshot.await_count == 1
    await coordinator.async_shutdown()


async def test_targeted_new_runtime_replaces_old_state(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    new_runtime = replace(
        snapshot,
        status={"player": {"runtime": "page-2"}, "volume": 10},
        doctor=None,
    )
    client.async_snapshot.return_value = new_runtime
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await command_observations_finished(coordinator)
    assert coordinator.data["test-player"] is new_runtime
    assert coordinator.data["test-player"].doctor is None
    await coordinator.async_shutdown()


async def test_targeted_refresh_and_other_player_poll_preserve_both_results(hass, client, snapshot):
    coordinator = OttplayCoordinator(hass, make_entry(["test-player", "other-player"]), client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot, "other-player": snapshot})
    coordinator._next_poll["test-player"] = time.monotonic() + 3600
    entered, release = asyncio.Event(), asyncio.Event()
    target_fresh = replace(snapshot, status={**snapshot.status, "volume": 75})
    other_fresh = replace(snapshot, status={**snapshot.status, "volume": 20})

    async def read(device_id):
        if device_id == "other-player":
            entered.set()
            await release.wait()
            return other_fresh
        return target_fresh

    client.async_snapshot.side_effect = read
    poll = asyncio.create_task(coordinator._async_update_data())
    await entered.wait()
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await command_observations_finished(coordinator)
    assert coordinator.data == {"test-player": target_fresh, "other-player": snapshot}
    release.set()
    coordinator.async_set_updated_data(await poll)
    assert coordinator.data == {"test-player": target_fresh, "other-player": other_fresh}
    await coordinator.async_shutdown()


async def test_targeted_auth_failure_starts_reauth(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    client.async_snapshot.side_effect = AuthError()
    with patch.object(type(entry), "async_start_reauth") as reauth:
        await coordinator.async_command("test-player", "input", {"key": "ok"})
        await command_observations_finished(coordinator)
        reauth.assert_called_once_with(hass)
    assert coordinator.data["test-player"] is None
    assert not coordinator.last_update_success
    assert client.async_call.await_count == client.async_snapshot.await_count == 1
    await coordinator.async_shutdown()


@pytest.mark.parametrize("global_error", [ConfigEntryAuthFailed, UpdateFailed])
@pytest.mark.parametrize("target_fails", [False, True])
async def test_targeted_result_cannot_recover_failed_fleet_refresh(
    hass, client, snapshot, global_error, target_fails
):
    from custom_components.ottplay.media_player import OttplayMediaPlayer

    coordinator = OttplayCoordinator(hass, make_entry(["test-player", "other-player"]), client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot, "other-player": snapshot})
    other = OttplayMediaPlayer(coordinator, "other-player")
    entered, release = asyncio.Event(), asyncio.Event()
    availability = []
    unsubscribe = coordinator.async_add_listener(lambda: availability.append(other.available))

    async def read(device_id):
        entered.set()
        await release.wait()
        if target_fails:
            raise PlayerUnavailable()
        return snapshot

    client.async_snapshot.side_effect = read
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await entered.wait()
    coordinator.async_set_update_error(global_error("Fleet refresh failed"))
    assert not other.available
    release.set()
    await command_observations_finished(coordinator)
    assert coordinator.data["test-player"] is (None if target_fails else snapshot)
    assert coordinator.data["other-player"] is snapshot
    assert not coordinator.last_update_success and not other.available
    assert availability and not any(availability)
    # Only a subsequent successful fleet refresh restores global health.
    client.async_snapshot.side_effect = None
    client.async_snapshot.return_value = snapshot
    await coordinator.async_refresh()
    assert coordinator.last_update_success and other.available
    unsubscribe()
    await coordinator.async_shutdown()


async def test_other_target_cannot_clear_targeted_auth_failure(hass, client, snapshot):
    entry = make_entry(["test-player", "other-player"])
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot, "other-player": snapshot})
    entered = {key: asyncio.Event() for key in ("test-player", "other-player")}
    release = {key: asyncio.Event() for key in entered}

    async def read(device_id):
        entered[device_id].set()
        await release[device_id].wait()
        if device_id == "test-player":
            raise AuthError()
        return snapshot

    client.async_snapshot.side_effect = read
    with patch.object(type(entry), "async_start_reauth") as reauth:
        for key in entered:
            await coordinator.async_command(key, "input", {"key": "ok"})
            await entered[key].wait()
        release["test-player"].set()
        await coordinator._command_refresh_tasks["test-player"]
        assert not coordinator.last_update_success
        release["other-player"].set()
        await command_observations_finished(coordinator)
        reauth.assert_called_once_with(hass)
    assert coordinator.data["other-player"] is snapshot
    assert not coordinator.last_update_success
    await coordinator.async_shutdown()


async def test_older_full_refresh_cannot_clear_new_target_auth_failure(hass, client, snapshot):
    """Exercise HA's real _async_refresh, which restores global health on success."""
    entry = make_entry(["test-player", "other-player"])
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot, "other-player": snapshot})
    coordinator._next_poll["test-player"] = time.monotonic() + 3600
    entered, release = asyncio.Event(), asyncio.Event()

    async def read(device_id):
        if device_id == "other-player":
            entered.set()
            await release.wait()
            return snapshot
        raise AuthError()

    client.async_snapshot.side_effect = read
    with (
        patch.object(type(entry), "async_start_reauth"),
        patch.object(type(entry), "async_start_reauth_if_available"),
    ):
        poll = asyncio.create_task(coordinator.async_refresh())
        await entered.wait()
        await coordinator.async_command("test-player", "input", {"key": "ok"})
        await command_observations_finished(coordinator)
        assert not coordinator.last_update_success
        release.set()
        await poll
        assert not coordinator.last_update_success
        assert coordinator.data["test-player"] is None
        assert isinstance(coordinator.last_exception, ConfigEntryAuthFailed)
        # A fresh fleet read is allowed to prove recovery at the new auth epoch.
        client.async_snapshot.side_effect = None
        client.async_snapshot.return_value = snapshot
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert coordinator.data["test-player"] is snapshot
    await coordinator.async_shutdown()


async def test_targeted_refresh_cannot_resurrect_removed_device(hass, client, snapshot):
    coordinator = OttplayCoordinator(hass, make_entry([]), client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot})
    entered, release = asyncio.Event(), asyncio.Event()

    async def read(device_id):
        entered.set()
        await release.wait()
        return snapshot

    client.async_snapshot.side_effect = read
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await entered.wait()
    client.async_devices.return_value = []
    coordinator.async_set_updated_data(await coordinator._async_update_data())
    assert coordinator.data["test-player"] is None
    release.set()
    await command_observations_finished(coordinator)
    assert coordinator.data["test-player"] is None
    assert client.async_snapshot.await_count == 1
    await coordinator.async_shutdown()


async def test_shutdown_cancels_targeted_refresh_without_followup(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    entered, cancelled = asyncio.Event(), asyncio.Event()

    async def read(device_id):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    client.async_snapshot.side_effect = read
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    await entered.wait()
    await coordinator.async_command("test-player", "input", {"key": "back"})
    await coordinator.async_shutdown()
    assert cancelled.is_set()
    assert not coordinator._command_refresh_tasks
    assert coordinator.data["test-player"] is snapshot
    assert client.async_snapshot.await_count == 1


async def test_shutdown_clears_targeted_task_before_it_starts(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    assert coordinator._command_refresh_tasks
    client.async_snapshot.assert_not_awaited()
    await coordinator.async_shutdown()
    assert not coordinator._command_refresh_tasks
    client.async_snapshot.assert_not_awaited()

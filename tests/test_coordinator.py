"""Fleet fairness, offline handling, lifecycle and mutation boundaries."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock

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


async def test_sequence_once_and_failure_invalidates_observation(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator.async_set_updated_data({"test-player": snapshot})
    coordinator.async_request_refresh = AsyncMock()
    await coordinator.async_commands(
        "test-player", [("input", {"key": "ok"}), ("input", {"key": "back"})]
    )
    assert client.async_call.await_count == 2
    assert coordinator.data["test-player"] is None
    with pytest.raises(ServiceValidationError):
        await coordinator.async_command("test-player", "playback", {"operation": "pause"})
    coordinator.async_set_updated_data({"test-player": snapshot})
    client.async_call.side_effect = PlayerUnavailable()
    with pytest.raises(HomeAssistantError):
        await coordinator.async_command("test-player", "playback", {"operation": "pause"})
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


async def test_snapshot_cannot_restore_state_from_before_command(hass, entry, client, snapshot):
    coordinator = OttplayCoordinator(hass, entry, client)
    coordinator._initialized = True
    coordinator.async_set_updated_data({"test-player": snapshot})
    coordinator.async_request_refresh = AsyncMock()
    entered, release = asyncio.Event(), asyncio.Event()

    async def slow_snapshot(device_id):
        entered.set()
        await release.wait()
        return snapshot

    client.async_snapshot.side_effect = slow_snapshot
    refresh = asyncio.create_task(coordinator._async_update_data())
    await entered.wait()
    await coordinator.async_command("test-player", "input", {"key": "ok"})
    release.set()
    result = await refresh
    assert result["test-player"] is None
    assert coordinator._next_poll["test-player"] == -1
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
    assert coordinator.data["test-player"] is None
    coordinator.async_request_refresh.assert_not_awaited()
    await coordinator.async_shutdown()

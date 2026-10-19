"""Media properties report observations; commands are never guessed or replayed."""

from dataclasses import replace
from unittest.mock import AsyncMock

import pytest
from homeassistant.components.media_player import MediaPlayerEntityFeature as Feature
from homeassistant.components.media_player import MediaPlayerState, MediaType
from homeassistant.exceptions import ServiceValidationError

from custom_components.ottplay.coordinator import OttplayCoordinator
from custom_components.ottplay.diagnostics import async_get_config_entry_diagnostics
from custom_components.ottplay.media_player import OttplayMediaPlayer
from custom_components.ottplay.remote import OttplayRemote


@pytest.fixture
async def coordinator(hass, entry, client, snapshot):
    value = OttplayCoordinator(hass, entry, client)
    value.async_set_updated_data({"test-player": snapshot})
    yield value
    await value.async_shutdown()


def test_observed_media(coordinator, snapshot):
    entity = OttplayMediaPlayer(coordinator, "test-player")
    assert entity.available
    assert entity.state == MediaPlayerState.PLAYING
    assert entity.volume_level == 0.4
    assert entity.media_content_type == MediaType.VIDEO
    assert entity.media_position == 15 and entity.media_duration == 60
    assert entity.media_position_updated_at == snapshot.observed_at
    assert entity.supported_features & Feature.SEEK
    assert entity.supported_features & Feature.PLAY_MEDIA
    assert not entity.supported_features & (
        Feature.TURN_ON | Feature.TURN_OFF | Feature.STOP | Feature.VOLUME_MUTE
    )
    assert entity.media_title is None
    assert entity.device_info["sw_version"] == "1.1.56"
    coordinator.async_set_updated_data({"test-player": None})
    assert not entity.available and entity.state is None
    assert entity.supported_features == 0 and entity.volume_level is None


@pytest.mark.parametrize(
    "doctor",
    [
        None,
        {"consistent": False, "media": {"phase": "playing"}},
        {"consistent": True, "media": {"phase": "unknown"}},
    ],
)
def test_no_invented_state(coordinator, snapshot, doctor):
    coordinator.async_set_updated_data({"test-player": replace(snapshot, doctor=doctor)})
    entity = OttplayMediaPlayer(coordinator, "test-player")
    assert entity.available and entity.state is None
    assert entity.media_position is None


@pytest.mark.parametrize("volume", [True, "45", float("nan"), 101, -1, None])
def test_invalid_volume_never_exposed(coordinator, snapshot, volume):
    coordinator.async_set_updated_data(
        {"test-player": replace(snapshot, status={"volume": volume})}
    )
    entity = OttplayMediaPlayer(coordinator, "test-player")
    assert entity.volume_level is None
    assert not entity.supported_features & Feature.VOLUME_SET


async def test_media_actions(coordinator):
    coordinator.async_command = AsyncMock()
    entity = OttplayMediaPlayer(coordinator, "test-player")
    for method, operation in [
        (entity.async_media_play, "resume"),
        (entity.async_media_pause, "pause"),
        (entity.async_media_next_track, "next_channel"),
        (entity.async_media_previous_track, "previous_channel"),
    ]:
        await method()
        coordinator.async_command.assert_awaited_with(
            "test-player", "playback", {"operation": operation}
        )
    await entity.async_media_seek(32.5)
    coordinator.async_command.assert_awaited_with(
        "test-player", "playback", {"operation": "seek", "position": 32.5}
    )
    await entity.async_set_volume_level(0.75)
    coordinator.async_command.assert_awaited_with(
        "test-player", "command", {"command": "set_volume", "volume": 75}
    )
    await entity.async_play_media("channel", "  News ")
    coordinator.async_command.assert_awaited_with("test-player", "play", {"query": "News"})


async def test_reject_unsupported_and_invalid_actions(coordinator, snapshot):
    coordinator.async_command = AsyncMock()
    entity = OttplayMediaPlayer(coordinator, "test-player")
    for value in [-1, float("nan"), float("inf")]:
        with pytest.raises(ServiceValidationError):
            await entity.async_media_seek(value)
    for kind, media in [("url", "https://private.example"), ("channel", ""), ("channel", "1\n2")]:
        with pytest.raises(ServiceValidationError):
            await entity.async_play_media(kind, media)
    with pytest.raises(ServiceValidationError):
        await entity.async_play_media("channel", "1", enqueue="add")
    coordinator.async_set_updated_data({"test-player": replace(snapshot, capabilities={})})
    with pytest.raises(ServiceValidationError):
        await entity.async_media_pause()
    coordinator.async_command.assert_not_awaited()


async def test_remote_validates_whole_sequence_and_delay(coordinator):
    coordinator.async_commands = AsyncMock()
    entity = OttplayRemote(coordinator, "test-player")
    assert entity.is_on
    await entity.async_send_command(["ok", "down", "back"], delay_secs=0.5)
    coordinator.async_commands.assert_awaited_once_with(
        "test-player",
        [("input", {"key": "ok"}), ("input", {"key": "down"}), ("input", {"key": "back"})],
        delay=0.5,
    )
    for keys, args in [
        (["up", "not-a-key"], {}),
        (["up"], {"hold_secs": 1}),
        (["up"], {"num_repeats": 2}),
        (["up"], {"delay_secs": 99}),
        ([], {}),
    ]:
        with pytest.raises(ServiceValidationError):
            await entity.async_send_command(keys, **args)
    assert coordinator.async_commands.await_count == 1


async def test_diagnostics_no_secrets(hass, entry, coordinator):
    import json

    entry.runtime_data = coordinator
    encoded = json.dumps(await async_get_config_entry_diagnostics(hass, entry))
    for value in [entry.entry_id, "test-player", "control.example", "a" * 32, "page-1", "1.1.56"]:
        assert value not in encoded

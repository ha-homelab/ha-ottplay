"""Real HA runtime with synthetic data and no credentials or device traffic."""

from datetime import datetime, timezone
from types import MappingProxyType
from unittest.mock import AsyncMock

import pytest
from homeassistant.config_entries import ConfigEntries, ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.ottplay.api import PlayerSnapshot


@pytest.fixture
async def hass(tmp_path):
    instance = HomeAssistant(str(tmp_path))
    instance.config_entries = ConfigEntries(instance, {})
    yield instance
    await instance.async_stop(force=True)
    await instance.async_block_till_done()


def make_entry(devices=None):
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain="ottplay",
        title="OTTPlay test",
        data={
            "url": "http://control.example",
            "token": "a" * 32,
            "devices": devices if devices is not None else ["test-player"],
        },
        source="user",
        unique_id="http://control.example",
        options={},
        discovery_keys=MappingProxyType({}),
        subentries_data=[],
    )


@pytest.fixture
def entry():
    return make_entry()


@pytest.fixture
def snapshot():
    return PlayerSnapshot(
        status={
            "player": {"runtime": "page-1", "version": "1.1.56", "platform": "browser"},
            "ready": True,
            "volume": 40,
        },
        capabilities={
            "playback": ["pause", "resume", "seek", "previous_channel", "next_channel"],
            "input": ["up", "down", "left", "right", "ok", "back", "red"],
        },
        doctor={
            "consistent": True,
            "media": {
                "phase": "playing",
                "kind": "vod",
                "lanes": [{"lane": "main", "position": 15, "duration": 60}],
            },
        },
        observed_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def client(snapshot):
    value = AsyncMock()
    value.url = "http://control.example"
    value.async_snapshot.return_value = snapshot
    value.async_call.return_value = {"dispatched": True}
    return value

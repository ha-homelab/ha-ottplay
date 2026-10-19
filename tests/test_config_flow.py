"""Exercise actual HA config flows, entities, reconfiguration and unloading."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from homeassistant import loader
from homeassistant.bootstrap import async_load_base_functionality
from homeassistant.helpers import device_registry as dr

from custom_components.ottplay.api import AuthError, Device
from custom_components.ottplay.config_flow import parse_devices


@pytest.mark.parametrize("value", ["one,one", "a,,b", "bad/path", "a" * 129])
def test_device_input_invalid(value):
    with pytest.raises(ValueError):
        parse_devices(value)


def test_device_input_valid():
    assert parse_devices(" one, namespace:two ") == ["one", "namespace:two"]
    assert parse_devices("  ") == []


async def bootstrap(hass):
    Path(hass.config.path("custom_components")).symlink_to(
        Path(__file__).resolve().parents[1] / "custom_components", target_is_directory=True
    )
    loader.async_setup(hass)
    assert await async_load_base_functionality(hass)


async def test_real_ha_setup_reconfigure_discovery_and_unload(hass, snapshot):
    await bootstrap(hass)
    devices = [Device("test-player", datetime.now(timezone.utc))]
    with (
        patch("custom_components.ottplay.config_flow.async_get_clientsession", return_value=None),
        patch("custom_components.ottplay.async_get_clientsession", return_value=None),
        patch("custom_components.ottplay.api.OttplayClient.async_devices", return_value=devices),
        patch("custom_components.ottplay.api.OttplayClient.async_snapshot", return_value=snapshot),
    ):
        result = await hass.config_entries.flow.async_init("ottplay", context={"source": "user"})
        assert result["step_id"] == "user"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"url": "http://control.example", "token": "a" * 32, "devices": ""}
        )
        assert result["type"] == "create_entry"
        await hass.async_block_till_done()
        entry = hass.config_entries.async_entries("ottplay")[0]
        await entry.runtime_data.async_refresh()
        await hass.async_block_till_done()
        players = hass.states.async_all("media_player")
        assert len(players) == 1 and players[0].state == "playing"
        assert len(hass.states.async_all("remote")) == 1
        entity_id = players[0].entity_id
        registry = dr.async_get(hass)
        registered = registry.async_get_device(
            identifiers={("ottplay", f"{entry.entry_id}:test-player")}
        )
        registry.async_update_device(registered.id, name_by_user="My chosen player")
        # The token changes through the actual reauthentication flow.
        flow = await hass.config_entries.flow.async_init(
            "ottplay", context={"source": "reauth", "entry_id": entry.entry_id}, data=entry.data
        )
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {"url": "http://control.example", "token": "b" * 32, "devices": ""}
        )
        assert result["reason"] == "reauth_successful"
        await hass.async_block_till_done()
        assert entry.data["token"] == "b" * 32
        flow = await hass.config_entries.flow.async_init(
            "ottplay", context={"source": "reconfigure", "entry_id": entry.entry_id}
        )
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {"url": "http://replacement.example", "token": "c" * 32, "devices": ""}
        )
        assert result["reason"] == "reconfigure_successful"
        await hass.async_block_till_done()
        await entry.runtime_data.async_refresh()
        assert entry.unique_id == "http://replacement.example"
        assert hass.states.get(entity_id) is not None
        assert registry.async_get(registered.id).name_by_user == "My chosen player"
        devices.append(Device("second", None))
        await entry.runtime_data.async_refresh()
        await hass.async_block_till_done()
        assert len(hass.states.async_all("media_player")) == 2
        assert any(state.state == "unavailable" for state in hass.states.async_all("media_player"))
        assert await hass.config_entries.async_unload(entry.entry_id)
        assert all(state.state == "unavailable" for state in hass.states.async_all("media_player"))


async def test_real_flow_auth_error_no_entry(hass):
    await bootstrap(hass)
    with (
        patch("custom_components.ottplay.config_flow.async_get_clientsession", return_value=None),
        patch("custom_components.ottplay.api.OttplayClient.async_devices", side_effect=AuthError),
    ):
        flow = await hass.config_entries.flow.async_init("ottplay", context={"source": "user"})
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {"url": "http://control.example", "token": "a" * 32}
        )
        assert result["errors"] == {"base": "invalid_auth"}
        assert not hass.config_entries.async_entries("ottplay")

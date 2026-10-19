"""OTTPlay Control Server integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OttplayClient
from .coordinator import OttplayCoordinator

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.REMOTE]
type OttplayConfigEntry = ConfigEntry[OttplayCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: OttplayConfigEntry) -> bool:
    """Create one shared client and coordinator for the server."""
    client = OttplayClient(
        async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_TOKEN]
    )
    coordinator = OttplayCoordinator(hass, entry, client)
    entry.runtime_data = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_create_background_task(
        hass, coordinator.async_request_refresh(), "OTTPlay initial observations"
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: OttplayConfigEntry) -> bool:
    """Remove platform listeners and stop coordinator polling."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

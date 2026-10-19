"""Allowlisted diagnostics exclude credentials and viewing history."""

from homeassistant.loader import async_get_integration

from .const import DOMAIN

PLAYBACK_OPERATIONS = frozenset(
    {"pause", "resume", "seek", "previous_channel", "next_channel", "step_channel"}
)


async def async_get_config_entry_diagnostics(hass, entry):
    integration = await async_get_integration(hass, DOMAIN)
    coordinator = getattr(entry, "runtime_data", None)
    snapshots = (coordinator.data or {}) if coordinator else {}
    return {
        "integration_version": str(integration.version),
        "last_update_success": bool(coordinator and coordinator.last_update_success),
        "registered_players": len(snapshots),
        "available_players": sum(value is not None for value in snapshots.values()),
        "players": [
            {
                "available": value is not None,
                "inspection_supported": bool(value and value.doctor is not None),
                "playback_operations": sorted(
                    PLAYBACK_OPERATIONS.intersection(value.capabilities.get("playback", []))
                )
                if value
                else [],
            }
            for value in snapshots.values()
        ],
    }

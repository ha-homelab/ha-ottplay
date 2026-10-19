"""Allowlisted diagnostics exclude credentials and viewing history."""


async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = getattr(entry, "runtime_data", None)
    snapshots = (coordinator.data or {}) if coordinator else {}
    return {
        "integration_version": "0.1.0",
        "last_update_success": bool(coordinator and coordinator.last_update_success),
        "registered_players": len(snapshots),
        "available_players": sum(value is not None for value in snapshots.values()),
        "players": [
            {
                "available": value is not None,
                "inspection_supported": bool(value and value.doctor is not None),
                "playback_operations": sorted(value.capabilities.get("playback", []))
                if value
                else [],
            }
            for value in snapshots.values()
        ],
    }

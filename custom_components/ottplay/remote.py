"""Navigation keys for the same registered OTTPlay player."""

import math
from collections.abc import Iterable
from typing import Any

from homeassistant.components.remote import RemoteEntity
from homeassistant.exceptions import ServiceValidationError

from .entity import OttplayEntity, register_devices

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    register_devices(entry.runtime_data, async_add_entities, OttplayRemote)


class OttplayRemote(OttplayEntity, RemoteEntity):
    _attr_translation_key = "navigation"

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id, "remote")

    @property
    def is_on(self) -> bool:
        """Remote connectivity, never the physical television power state."""
        return self.available

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        commands = list(command)
        if not commands or len(commands) > 20:
            raise ServiceValidationError("Send between one and twenty navigation keys")
        if kwargs.get("num_repeats", 1) != 1 or kwargs.get("hold_secs", 0):
            raise ServiceValidationError("Key repeats and holding are unsupported")
        allowed = self.snapshot.capabilities.get("input", []) if self.snapshot else []
        if any(key not in allowed for key in commands):
            raise ServiceValidationError("Navigation key is unavailable")
        delay = kwargs.get("delay_secs", 0)
        if not isinstance(delay, (int, float)) or not math.isfinite(delay) or not 0 <= delay <= 10:
            raise ServiceValidationError("Invalid delay between keys")
        await self.coordinator.async_commands(
            self.device_id, [("input", {"key": key}) for key in commands], delay=delay
        )

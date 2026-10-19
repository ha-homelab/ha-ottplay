"""Shared identity and availability for each registered player."""

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PlayerSnapshot
from .const import DOMAIN
from .coordinator import OttplayCoordinator


class OttplayEntity(CoordinatorEntity[OttplayCoordinator]):
    """A device identity survives renames, reconnects, and page reloads."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: OttplayCoordinator, device_id: str, suffix: str) -> None:
        super().__init__(coordinator, context=device_id)
        self.device_id = device_id
        self._attr_unique_id = f"{coordinator.entry.entry_id}:{device_id}:{suffix}"

    @property
    def snapshot(self) -> PlayerSnapshot | None:
        return (self.coordinator.data or {}).get(self.device_id)

    @property
    def available(self) -> bool:
        return super().available and self.snapshot is not None

    @property
    def device_info(self) -> DeviceInfo:
        info = self.snapshot.status.get("player", {}) if self.snapshot else {}
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.entry.entry_id}:{self.device_id}")},
            name=self.device_id,
            manufacturer="OTTPlay",
            model=info.get("platform") or "Player",
            sw_version=info.get("version"),
            configuration_url=self.coordinator.client.url,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.snapshot:
            registry = dr.async_get(self.hass)
            device = registry.async_get_device_by_identifier(
                (DOMAIN, f"{self.coordinator.entry.entry_id}:{self.device_id}"),
                self.coordinator.entry.entry_id,
            )
            info = self.snapshot.status.get("player", {})
            if device is not None:
                updates = {
                    key: value
                    for key, value in {
                        "model": info.get("platform"),
                        "sw_version": info.get("version"),
                    }.items()
                    if value and getattr(device, key) != value
                }
                if updates:
                    registry.async_update_device(device.id, **updates)
        super()._handle_coordinator_update()


def register_devices(coordinator, async_add_entities, factory):
    """Add newly registered players without reloading the integration."""
    known: set[str] = set()

    def add_new() -> None:
        added = set(coordinator.data or {}) - known
        if added:
            known.update(added)
            async_add_entities([factory(coordinator, device_id) for device_id in sorted(added)])

    add_new()
    coordinator.entry.async_on_unload(coordinator.async_add_listener(add_new))

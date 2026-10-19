"""Bounded polling shared by all entities belonging to a control server."""

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import AuthError, OttplayClient, OttplayError, PlayerSnapshot
from .const import CONF_DEVICES, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class OttplayCoordinator(DataUpdateCoordinator[dict[str, PlayerSnapshot | None]]):
    """Keep offline devices, while never retaining stale media observations."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: OttplayClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=5),
            always_update=False,
        )
        self.client = client
        self.entry = entry
        self._initialized = False
        self._next_poll: dict[str, float] = {}
        self._generation: dict[str, int] = {}
        self._command_locks: dict[str, asyncio.Lock] = {}

    async def _async_update_data(self) -> dict[str, PlayerSnapshot | None]:
        generation = dict(self._generation)
        try:
            configured = self.entry.data.get(CONF_DEVICES, [])
            if configured:
                active = set(configured)
                device_ids = configured
            else:
                devices = await self.client.async_devices()
                device_ids = [device.id for device in devices]
                now = dt_util.utcnow()
                active = {
                    device.id
                    for device in devices
                    if device.last_seen is not None
                    and timedelta(seconds=-30) <= now - device.last_seen < timedelta(seconds=120)
                }
            # Keep registry entities unavailable if the server removes their IDs.
            result = {
                key: (self.data or {}).get(key) if key in active else None
                for key in set(self.data or {}) | set(device_ids)
            }
            if not self._initialized:
                self._initialized = True
                return result
            now_mono = time.monotonic()
            due = sorted(
                (
                    key
                    for key in active
                    if self._next_poll.get(key, 0) <= now_mono
                    and not (key in self._command_locks and self._command_locks[key].locked())
                ),
                key=lambda key: (self._next_poll.get(key, 0), key),
            )[:4]
            semaphore = asyncio.Semaphore(4)

            async def update(device_id: str) -> None:
                async with semaphore:
                    try:
                        result[device_id] = await self.client.async_snapshot(device_id)
                        self._next_poll[device_id] = time.monotonic() + max(
                            DEFAULT_SCAN_INTERVAL, len(active) * 5
                        )
                    except AuthError:
                        raise
                    except OttplayError:
                        result[device_id] = None
                        self._next_poll[device_id] = time.monotonic() + 120

            async with asyncio.TaskGroup() as group:
                for device_id in due:
                    group.create_task(update(device_id))
            for key in result:
                if generation.get(key, 0) != self._generation.get(key, 0):
                    result[key] = None
                    self._next_poll[key] = -1
            return result
        except AuthError as err:
            raise ConfigEntryAuthFailed("OTTPlay authentication failed") from err
        except ExceptionGroup as err:
            if err.subgroup(AuthError):
                raise ConfigEntryAuthFailed("OTTPlay authentication failed") from None
            raise
        except OttplayError as err:
            raise UpdateFailed("Cannot reach OTTPlay Control Server") from err

    async def async_command(self, device_id: str, action: str, params: dict[str, Any]) -> dict:
        """Dispatch one command using the device sequence lock."""
        return (await self.async_commands(device_id, [(action, params)]))[0]

    async def async_commands(
        self, device_id: str, commands: list[tuple[str, dict]], delay: float = 0
    ) -> list[dict]:
        """Dispatch an explicit sequence once; never replay after an ambiguous failure."""
        if not self.last_update_success or not self.data or self.data.get(device_id) is None:
            raise ServiceValidationError("OTTPlay player is unavailable")
        lock = self._command_locks.setdefault(device_id, asyncio.Lock())
        if lock.locked():
            raise ServiceValidationError("An OTTPlay command is already in progress")
        async with lock:
            self._generation[device_id] = self._generation.get(device_id, 0) + 1
            try:
                responses = []
                for index, (action, params) in enumerate(commands):
                    if index and delay:
                        await asyncio.sleep(delay)
                    responses.append(await self.client.async_call(device_id, action, params))
            except AuthError:
                self.entry.async_start_reauth(self.hass)
                raise HomeAssistantError("OTTPlay authentication requires attention") from None
            except OttplayError:
                raise HomeAssistantError(
                    "OTTPlay command was not confirmed; inspect the player before retrying"
                ) from None
            finally:
                # Acknowledgement is not proof that the visible state changed.
                # Refresh observations without optimistically changing playback.
                self._generation[device_id] += 1
                self._next_poll[device_id] = -1
                self.async_set_updated_data({**self.data, device_id: None})
                task = asyncio.current_task()
                if task is None or not task.cancelling():
                    self.entry.async_create_background_task(
                        self.hass, self.async_request_refresh(), "OTTPlay command observations"
                    )
            return responses

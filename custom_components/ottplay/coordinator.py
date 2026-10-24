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
from .const import CONF_DEVICES, DEFAULT_SCAN_INTERVAL, DOMAIN, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class OttplayCoordinator(DataUpdateCoordinator[dict[str, PlayerSnapshot | None]]):
    """Keep observations until replaced, and mark failed observations unavailable."""

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
        self._command_refresh_tasks: dict[str, asyncio.Task[None]] = {}
        self._active_devices: set[str] | None = None
        self._auth_generation = 0
        self._stopped = False

    async def async_shutdown(self) -> None:
        """Cancel targeted observations along with ordinary polling."""
        self._stopped = True
        await super().async_shutdown()
        tasks = tuple(self._command_refresh_tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._command_refresh_tasks.clear()

    async def _async_update_data(self) -> dict[str, PlayerSnapshot | None]:
        generation = dict(self._generation)
        auth_generation = self._auth_generation
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
            self._active_devices = active
            # Keep registry entities unavailable if the server removes their IDs.
            result = {
                key: (self.data or {}).get(key) if key in active else None
                for key in set(self.data or {}) | set(device_ids)
            }
            if not self._initialized:
                self._initialized = True
                if auth_generation != self._auth_generation:
                    raise ConfigEntryAuthFailed("OTTPlay authentication failed")
                return result
            now_mono = time.monotonic()
            due = sorted(
                (
                    key
                    for key in active
                    if self._next_poll.get(key, 0) <= now_mono
                    and not (key in self._command_locks and self._command_locks[key].locked())
                    and key not in self._command_refresh_tasks
                ),
                key=lambda key: (self._next_poll.get(key, 0), key),
            )[:4]
            semaphore = asyncio.Semaphore(4)

            async def update(device_id: str) -> None:
                async with semaphore:
                    if (
                        generation.get(device_id, 0) != self._generation.get(device_id, 0)
                        or device_id in self._command_refresh_tasks
                    ):
                        return
                    try:
                        snapshot = await self.client.async_snapshot(device_id)
                        if generation.get(device_id, 0) != self._generation.get(device_id, 0):
                            return
                        result[device_id] = snapshot
                        self._next_poll[device_id] = time.monotonic() + max(
                            DEFAULT_SCAN_INTERVAL, len(active) * 5
                        )
                    except AuthError:
                        raise
                    except OttplayError:
                        if generation.get(device_id, 0) != self._generation.get(device_id, 0):
                            return
                        result[device_id] = None
                        self._next_poll[device_id] = time.monotonic() + 120

            async with asyncio.TaskGroup() as group:
                for device_id in due:
                    group.create_task(update(device_id))
            for key in result:
                if key in active and generation.get(key, 0) != self._generation.get(key, 0):
                    # A command or targeted observation superseded this poll.
                    # Keep the current observation, including a confirmed failure.
                    result[key] = (self.data or {}).get(key)
            if auth_generation != self._auth_generation:
                # An older fleet refresh must not clear a newer targeted auth error.
                raise ConfigEntryAuthFailed("OTTPlay authentication failed")
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
                # Keep the last observation until a targeted read replaces it.
                self._generation[device_id] += 1
                self._next_poll[device_id] = -1
                task = asyncio.current_task()
                if task is None or not task.cancelling():
                    self._schedule_command_refresh(device_id)
            return responses

    def _schedule_command_refresh(self, device_id: str) -> None:
        """Coalesce observations of successive commands without queuing commands."""
        if (
            self._stopped
            or self.hass.is_stopping
            or device_id in self._command_refresh_tasks
            or (self._active_devices is not None and device_id not in self._active_devices)
        ):
            return
        self._command_refresh_tasks[device_id] = self.entry.async_create_background_task(
            self.hass,
            self._async_refresh_after_command(device_id),
            "OTTPlay command observations",
            eager_start=False,  # Begin only after the command releases its sequence lock.
        )

    async def _async_refresh_after_command(self, device_id: str) -> None:
        """Read only the changed player, independently of fleet polling/debouncing."""
        generation = self._generation.get(device_id, 0)
        superseded = False
        auth_failed = False
        try:
            if self._command_locks[device_id].locked():
                return  # The in-progress command will schedule its own observation.
            try:
                # A snapshot contains at most three individually bounded RPCs.
                async with asyncio.timeout(3 * REQUEST_TIMEOUT):
                    snapshot = await self.client.async_snapshot(device_id)
            except AuthError:
                snapshot = None
                auth_failed = True
            except OttplayError, TimeoutError:
                snapshot = None
            if generation != self._generation.get(device_id, 0):
                superseded = True
                return
            if self._active_devices is not None and device_id not in self._active_devices:
                return
            # Fence an ordinary poll that started before this result was published.
            self._generation[device_id] = generation + 1
            self._next_poll[device_id] = time.monotonic() + (
                DEFAULT_SCAN_INTERVAL if snapshot is not None else 120
            )
            # A single player's result does not recover a failed fleet refresh.
            # Keep global health and the regular polling schedule unchanged.
            self.data = {**(self.data or {}), device_id: snapshot}
            if auth_failed:
                # A later fleet refresh must authenticate again, not recover
                # global health merely by returning its cached observations.
                self._next_poll[device_id] = -1
                self._auth_generation += 1
                self.entry.async_start_reauth(self.hass)
                self.async_set_update_error(ConfigEntryAuthFailed("OTTPlay authentication failed"))
            else:
                self.async_update_listeners()
        finally:
            self._command_refresh_tasks.pop(device_id, None)
            if superseded and not self._command_locks[device_id].locked():
                self._schedule_command_refresh(device_id)

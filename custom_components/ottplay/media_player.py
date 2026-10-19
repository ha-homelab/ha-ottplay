"""Media controls backed by reported capabilities and actual observations."""

import math
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.exceptions import ServiceValidationError

from .entity import OttplayEntity, register_devices

PARALLEL_UPDATES = 0
FEATURES = {
    "pause": MediaPlayerEntityFeature.PAUSE,
    "resume": MediaPlayerEntityFeature.PLAY,
    "seek": MediaPlayerEntityFeature.SEEK,
    "previous_channel": MediaPlayerEntityFeature.PREVIOUS_TRACK,
    "next_channel": MediaPlayerEntityFeature.NEXT_TRACK,
}
STATES = {
    "playing": MediaPlayerState.PLAYING,
    "paused": MediaPlayerState.PAUSED,
    "loading": MediaPlayerState.BUFFERING,
    "idle": MediaPlayerState.IDLE,
    "stopped": MediaPlayerState.IDLE,
    "ended": MediaPlayerState.IDLE,
}


async def async_setup_entry(hass, entry, async_add_entities):
    register_devices(entry.runtime_data, async_add_entities, OttplayMediaPlayer)


class OttplayMediaPlayer(OttplayEntity, MediaPlayerEntity):
    _attr_name = None
    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_app_name = "OTTPlay"

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id, "player")

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        features = MediaPlayerEntityFeature(0)
        if not (snapshot := self.snapshot):
            return features
        for operation in snapshot.capabilities.get("playback", []):
            features |= FEATURES.get(operation, MediaPlayerEntityFeature(0))
        if self.volume_level is not None:
            features |= MediaPlayerEntityFeature.VOLUME_SET
        if snapshot.status.get("ready") is True:
            features |= MediaPlayerEntityFeature.PLAY_MEDIA
        return features

    @property
    def state(self) -> MediaPlayerState | None:
        if not self.snapshot or not self.snapshot.doctor:
            return None
        doctor = self.snapshot.doctor
        if doctor.get("consistent") is not True:
            return None
        return STATES.get(doctor.get("media", {}).get("phase"))

    @property
    def volume_level(self) -> float | None:
        value = self.snapshot.status.get("volume") if self.snapshot else None
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and 0 <= value <= 100
        ):
            return value / 100
        return None

    @property
    def media_content_type(self) -> MediaType | None:
        kind = (
            self.snapshot.doctor.get("media", {}).get("kind")
            if self.snapshot and self.snapshot.doctor
            else None
        )
        return {"live": MediaType.CHANNEL, "archive": MediaType.VIDEO, "vod": MediaType.VIDEO}.get(
            kind
        )

    def _lane_value(self, key: str) -> float | None:
        if (
            not self.snapshot
            or not self.snapshot.doctor
            or self.snapshot.doctor.get("consistent") is not True
        ):
            return None
        for lane in self.snapshot.doctor.get("media", {}).get("lanes", []):
            if lane.get("lane") == "main":
                value = lane.get(key)
                if (
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                    and value >= 0
                ):
                    return value
        return None

    @property
    def media_position(self) -> float | None:
        return self._lane_value("position")

    @property
    def media_duration(self) -> float | None:
        return self._lane_value("duration")

    @property
    def media_position_updated_at(self):
        return (
            self.snapshot.observed_at if self.snapshot and self.media_position is not None else None
        )

    async def _playback(self, operation: str, **params: Any) -> None:
        if not self.snapshot or operation not in self.snapshot.capabilities.get("playback", []):
            raise ServiceValidationError("Operation is unavailable for this player")
        await self.coordinator.async_command(
            self.device_id, "playback", {"operation": operation, **params}
        )

    async def async_media_play(self) -> None:
        await self._playback("resume")

    async def async_media_pause(self) -> None:
        await self._playback("pause")

    async def async_media_next_track(self) -> None:
        await self._playback("next_channel")

    async def async_media_previous_track(self) -> None:
        await self._playback("previous_channel")

    async def async_media_seek(self, position: float) -> None:
        if not math.isfinite(position) or not 0 <= position <= 315576000:
            raise ServiceValidationError("Invalid seek position")
        await self._playback("seek", position=position)

    async def async_set_volume_level(self, volume: float) -> None:
        if not math.isfinite(volume) or not 0 <= volume <= 1 or self.volume_level is None:
            raise ServiceValidationError("Volume cannot be set")
        await self.coordinator.async_command(
            self.device_id, "command", {"command": "set_volume", "volume": round(volume * 100)}
        )

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None:
        # URLs, library IDs, announcements and queues have different semantics;
        # this version exposes only the existing TV catalogue selection action.
        if media_type != MediaType.CHANNEL or kwargs.get("enqueue") or kwargs.get("announce"):
            raise ServiceValidationError(
                "Use media_content_type channel with a channel number or name"
            )
        query = str(media_id).strip()
        if (
            not query
            or len(query.encode("utf-8")) > 1024
            or any(ord(c) < 32 or ord(c) == 127 for c in query)
        ):
            raise ServiceValidationError("Invalid channel query")
        if not self.snapshot or self.snapshot.status.get("ready") is not True:
            raise ServiceValidationError("Channel catalogue is not ready")
        await self.coordinator.async_command(self.device_id, "play", {"query": query})

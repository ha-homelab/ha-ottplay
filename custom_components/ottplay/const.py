"""Shared constants for the OTTPlay integration."""

DOMAIN = "ottplay"
CONF_DEVICES = "devices"
DEFAULT_SCAN_INTERVAL = 30
REQUEST_TIMEOUT = 15
MAX_DEVICES = 64
DEVICE_ID_PATTERN = r"[A-Za-z0-9_.:-]{1,128}"
INPUT_KEYS = (
    "up",
    "down",
    "left",
    "right",
    "ok",
    "back",
    "menu",
    "settings",
    "channels",
    "guide",
    "info",
    "channel_up",
    "channel_down",
    "volume_up",
    "volume_down",
    "mute",
    "play_pause",
    "audio",
    "aspect",
    "zoom",
    "pip",
    "fullscreen",
)
REQUIRED_ACTIONS = (
    "status",
    "capabilities",
    "inspect",
    "play",
    "command.set_volume",
    "playback.pause",
    "playback.resume",
    "playback.seek",
    "playback.previous_channel",
    "playback.next_channel",
    "playback.step_channel",
) + tuple("input." + key for key in INPUT_KEYS)

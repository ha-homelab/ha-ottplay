# Changelog

## [0.1.0]

Initial custom Home Assistant integration for registered OTTPlay players.

- Native media-player and remote entities using the existing controller API.
- Restricted operator configuration or administrator registry discovery.
- Runtime-bound playback observations, capability-aware controls, UI setup and reconfiguration.
- English and Russian documentation and translations, redacted diagnostics.
- Pinned dependencies, shared CI, HA validation and versioned release packages.

A current programme title and artwork are not available in the controller's
status contract. Hardware power control is outside this integration's scope.

### Upgrade

This is the initial integration release for Home Assistant 2026.10 or newer.
Add this repository to HACS as an integration, enable beta releases and install
the chosen candidate, then restart Home Assistant and add OTTPlay in Devices &
services. HACS uses `ottplay.zip`; manual installation uses `ha-ottplay.zip` and
its `custom_components/ottplay` directory. Configure the existing OTTPlay
Control Server and verify the discovered entities before using automations.
Back up any development installation and its configuration before replacing it.

### Security

Use a dedicated operator token scoped to the intended device IDs and commands;
administrator credentials are needed only for automatic registry discovery.
Keep credentials out of logs and shared diagnostics. Use HTTPS outside a trusted
local network and keep certificate verification enabled. A successful command
acknowledgement does not prove playback, picture or sound; physical power control
is not provided by this integration.

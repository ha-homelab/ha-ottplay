# Configuration and permissions

Configure the integration in Settings → Devices & services. The controller URL
is used by the Home Assistant server, not by your web browser. Localhost means
HA's own host or container. Use HTTPS for untrusted networks; a private cluster
service or trusted LAN can use HTTP. Normal certificate verification stays on.

## Restricted operator

The current controller supports command operators with an ID, a SHA-256 digest
of a dedicated random token, explicit `device_ids`, and explicit `actions`.
This is distinct from device polling credentials and diagnostic-only operators.
The integration needs the token itself, not its hash.

Read the controller's [command operator guide](https://github.com/open-ott-play/ottplay-control-server/blob/main/docs/api.md)
and validate the changed private controller configuration before restarting it.
Keep the token outside Git. Add the same device IDs to the integration form.
Only select players you intend to expose to Home Assistant users and automations.

The exact action grants used by this release are documented with the implementation
in `REQUIRED_ACTIONS` in `custom_components/ottplay/const.py`. The list includes
read-only status/capabilities/inspection, channel selection, playback operations,
volume adjustment and the enumerated navigation keys. Do not grant screenshots, provider-secret
access, updates or device reboot merely to use media controls.

Current server policy reserves `/api/devices` for administrators. Consequently,
a restricted installation needs a deliberate configuration update when a new
player is registered. The normal administrator CLI (`ott devices`) remains the
source of player IDs. Changing a player's page runtime does not require changing
its registered ID or HA entity.

## Administrator discovery

Leave the player-ID field empty to discover the controller registry. This mode
requires `admin_token`. It discovers registrations rather than scanning your LAN.
Do not use a per-player token: those authorize the opposite direction of traffic.
Names can be edited in Home Assistant's entity/device settings without changing IDs.

## Troubleshooting

- **Cannot connect:** verify the URL from HA's network, its path prefix, DNS,
  certificate chain and firewall. A reverse proxy must pass Authorization headers.
- **Invalid authentication:** use a command operator for the configured IDs, or
  the administrator token for registry discovery. Reconfigure after rotating it.
- **Unavailable player:** start the player and enable its existing Remote control
  connection. A registry entry is not evidence the page is running.
- **Missing controls:** the integration only exposes supported actions. Update the
  player/controller together; do not substitute a guessed key for a missing API.
- **State unknown:** the player cannot currently provide a bound doctor observation.
  This is different from stopped, paused or offline.
- **Timeout after pressing a button:** do not blindly repeat it. It may already
  have been applied. Wait for the next state observation.
- **No current title or artwork:** the current protocol does not report these fields.

Removing the integration deletes its HA configuration and entities; it does not
unregister the player from the controller. Revoke its dedicated operator on the
controller separately if access is no longer needed.

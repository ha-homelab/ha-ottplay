# Architecture and tradeoffs

![Architecture](diagrams/architecture.svg)

A single HA config entry represents one controller. The shared coordinator
updates device entities from its registered-player inventory or explicit
restricted-operator list. Requests use the existing asynchronous controller API:
submit once, wait for the same request ID, then validate the response.
A player restart changes its runtime ID; runtime-bound inspection must be refreshed.

The controller's `last_seen` is only connection evidence. Playback state comes
from `inspect` / `doctor` and numeric playback observations. Capabilities determine
which actions are advertised. Unsupported telemetry remains unknown rather than
being guessed from a sent command. Offline players cannot stall discovery of others.

## Why this design

**Direct integration:** reuses the installed controller, needs no new daemon,
creates native HA entities and shares polling among entities.

**MQTT bridge:** adds a service, credentials and state synchronization. HA's
[MQTT integration](https://www.home-assistant.io/integrations/mqtt/) does not provide
a native MQTT media-player discovery platform. It would still require a custom
media-player implementation or a less expressive abstraction.

**Connect to every TV:** requires per-platform listeners/network reachability and
additional credentials, bypassing the controller already paired with those players.

## Trust and lifecycle

The controller already has the player connection. HA receives only its own
operator token (recommended) and configured device IDs. Automatic full-registry
mode requires administrator credentials under the current server API.

All I/O is asynchronous and bounded. Polling is budgeted; a slow/offline player
must not create an unbounded task or request backlog. Unloading an entry removes
listeners and cancels its work. There is no periodic mutation and no automatic
retry of uncertain commands.

This project uses the official HA
[coordinator pattern](https://developers.home-assistant.io/docs/integration_fetching_data/),
[media-player contract](https://developers.home-assistant.io/docs/core/entity/media-player/)
and [configuration flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler/).

# OTTPlay for Home Assistant

[Русский](README.ru.md) · [Architecture](docs/architecture.md) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md)

Control registered OTTPlay players from Home Assistant through your existing
[OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server).
One connection gives each player a `media_player` entity and a `remote` entity.
The TV makes outbound requests to the controller; Home Assistant does not need
a listening port on the TV, an MQTT broker, or a second bridge process.

![How it works](docs/diagrams/architecture.svg)

## What you get

- Playback state read from the running player, with unavailable devices clearly marked.
- Play/pause, previous/next channel, seek and volume when supported by that player.
- Channel selection by number or name through `media_player.play_media`.
- Navigation through `remote.send_command`: arrows, OK, Back and other supported keys.
- UI configuration, credential replacement, English/Russian translations and redacted diagnostics.
- Stable entity identities, including across player restarts.

Capabilities depend on the player build, playback mode and connection.
Stop and hardware power buttons are not exposed: standby/wake can have different
semantics on each player and are not substituted for playback stop/resume. The
integration does not invent a current title, artwork or hardware power state.
A controller acknowledgement means the handler replied; it does not prove that
a picture is visible or sound is audible. State comes from a subsequent read.

## Install

Requires **Home Assistant 2026.10.0 or later** and a current OTTPlay Control Server
and player supporting the request/response API. This is a custom integration,
not part of Home Assistant Core and not a default HACS repository.

**HACS:** add `ha-homelab/ha-ottplay` as a custom repository of type **Integration**,
install **OTTPlay**, then restart Home Assistant. Enable prereleases in HACS when
installing a beta.

**Manual:** download `ha-ottplay.zip` from a
[release](https://github.com/ha-homelab/ha-ottplay/releases), verify its checksum,
and extract its `custom_components/ottplay` directory into your HA configuration
directory. Keep existing HA files. Restart Home Assistant.

Go to **Settings → Devices & services → Add integration → OTTPlay**.
Use a URL that Home Assistant itself can reach, including any controller path
prefix. For example, `https://controller.example.net/ott-control`.

Two authorization modes are supported:

1. **Restricted operator (recommended):** use a dedicated command-operator token
   and list its allowed player IDs in the configuration form. Obtain IDs from
   `ott devices`. Registering a new player does not silently expand this grant;
   update the server grant and integration configuration deliberately.
2. **Automatic registry:** leave player IDs empty and use the server administrator
   token. The integration reads the server registry and discovers new devices.
   This credential grants much broader access. Only use it with a trusted HA instance.

Device tokens and diagnostic-only operator tokens cannot be used here. See
[configuration and permissions](docs/configuration.md).

## Use in an automation

```yaml
action: media_player.play_media
target:
  entity_id: media_player.ottplay_living_room
data:
  media_content_type: channel
  media_content_id: "12"
```

```yaml
action: remote.send_command
target:
  entity_id: remote.ottplay_living_room
data:
  command: [ok, down, back]
```

Replace example entity IDs with those created on your system. Channel selection
uses the player's current provider; it does not upload an arbitrary media URL.
Configuration does not start playback or operate physical TV power.

## Development and releases

Use Python 3.14 and `uv sync --locked`, then `uv run pytest -q`,
`uv run ruff check .` and `uv run ruff format --check .`.
Tests exercise protocol failures, credentials, lifecycle and actual HA entity
services without connecting to household devices. See [release process](docs/releasing.md).

Public repository settings are managed in
[Terraform](https://github.com/4alvit/terraform-github-ha-homelab).
CI uses pinned shared workflows from
[venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

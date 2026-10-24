# OTTPlay for Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

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

**Troubleshooting state updates:** after a volume or playback command, the
integration keeps the last observed state while it reads the affected player
again. Command acceptance alone does not change the reported state, and a
pending confirmation does not make a connected player unavailable. A failed
observation or an actual loss of connection still makes the entity unavailable.

If your dashboard's **Other players** card excludes unavailable entities, a
player disappears from that card while unavailable and returns after a successful
observation. Sorting by friendly name only changes its position in the list.
Check the entity in **Developer tools → States** to distinguish a filtered card
from a missing entity.

After upgrading this integration, restart **Home Assistant Core** to load the
updated Python code. Reloading only the OTTPlay configuration entry recreates its
connection but does not replace Python modules already loaded in memory.

## Development and releases

Use Python 3.14 and `uv sync --locked`, then `uv run pytest -q`,
`uv run ruff check .` and `uv run ruff format --check .`.
Tests exercise protocol failures, credentials, lifecycle and actual HA entity
services without connecting to household devices. See [release process](docs/releasing.md).

Public repository settings are managed in
[Terraform](https://github.com/4alvit/terraform-github-ha-homelab).
CI uses pinned shared workflows from
[venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

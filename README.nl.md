# OTTPlay voor Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Architectuur](docs/architecture.md) · [Beveiliging](SECURITY.md) · [Bijdragen](CONTRIBUTING.md)

Bedien geregistreerde OTTPlay-spelers vanuit Home Assistant via je bestaande [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server). Eén verbinding geeft elke speler een `media_player`-entiteit en een `remote`-entiteit. De tv verstuurt uitgaande verzoeken naar de controller; Home Assistant heeft geen luisterende poort op de tv, MQTT-broker of tweede bridgeproces nodig.

![Werking](docs/diagrams/architecture.svg)

## Mogelijkheden

- Afspeelstatus uit de actieve speler, met duidelijke aanduiding van niet-beschikbare apparaten.
- Afspelen/pauzeren, vorig/volgend kanaal, zoeken in de tijdlijn en volume als de speler dit ondersteunt.
- Kanaalkeuze op nummer of naam via `media_player.play_media`.
- Navigatie via `remote.send_command`: pijlen, OK, Terug en andere ondersteunde toetsen.
- Configuratie via de interface, vervanging van inloggegevens, Engelse/Russische interfaceteksten en diagnostiek zonder gevoelige gegevens.
- Stabiele entiteitsidentiteiten, ook na het herstarten van de speler.

De mogelijkheden hangen af van de spelerversie, afspeelmodus en verbinding. Stop- en fysieke aan/uitknoppen worden niet aangeboden: stand-by/ontwaken kan per speler iets anders betekenen en vervangt afspelen stoppen/hervatten niet. De integratie verzint geen huidige titel, afbeeldingen of fysieke energiestatus. Een bevestiging van de controller betekent dat de handler heeft geantwoord; ze bewijst niet dat er beeld zichtbaar of geluid hoorbaar is. De status komt uit een latere uitlezing.

## Installatie

Vereist **Home Assistant 2026.10.0 of nieuwer**, een actuele OTTPlay Control Server en een speler die de verzoek/antwoord-API ondersteunt. Dit is een aangepaste integratie, geen onderdeel van Home Assistant Core en geen standaard HACS-repository.

**HACS:** voeg `ha-homelab/ha-ottplay` toe als aangepaste repository van het type **Integration**, installeer **OTTPlay** en herstart Home Assistant. Schakel voorlopige versies in HACS in om een bèta te installeren.

**Handmatig:** download `ha-ottplay.zip` uit een [release](https://github.com/ha-homelab/ha-ottplay/releases), controleer de controlesom en pak de map `custom_components/ottplay` uit in je HA-configuratiemap. Behoud bestaande HA-bestanden. Herstart Home Assistant.

Ga naar **Settings → Devices & services → Add integration → OTTPlay**. Gebruik een URL die Home Assistant zelf kan bereiken, inclusief een eventueel padprefix van de controller; bijvoorbeeld `https://controller.example.net/ott-control`.

Er zijn twee autorisatiemodi:

1. **Beperkte operator (aanbevolen):** gebruik een afzonderlijk token voor een commando-operator en vermeld de toegestane speler-ID's in het configuratieformulier. Haal ID's op met `ott devices`. Registratie van een nieuwe speler breidt deze toestemming niet stilzwijgend uit; werk de serverrechten en integratieconfiguratie bewust bij.
2. **Automatisch register:** laat de speler-ID's leeg en gebruik het beheerderstoken van de server. De integratie leest het serverregister en ontdekt nieuwe apparaten. Deze inloggegevens geven veel ruimere toegang. Gebruik ze alleen met een vertrouwde HA-instantie.

Apparaattokens en operatortokens die alleen diagnostiek toestaan, werken hier niet. Zie [configuratie en rechten](docs/configuration.md).

## Gebruik in een automatisering

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

Vervang de voorbeeld-ID's door de entiteits-ID's van je systeem. Kanaalkeuze gebruikt de huidige provider van de speler; er wordt geen willekeurige media-URL geüpload. Configuratie start geen weergave en schakelt de fysieke voeding van de tv niet.

## Ontwikkeling en releases

Gebruik Python 3.14 en `uv sync --locked`, daarna `uv run pytest -q`, `uv run ruff check .` en `uv run ruff format --check .`. Tests controleren protocolfouten, inloggegevens, levenscyclus en echte HA-entiteitsdiensten zonder verbinding met huishoudelijke apparaten. Zie het [releaseproces](docs/releasing.md).

De openbare repository-instellingen worden beheerd met [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI gebruikt vastgelegde gedeelde workflows uit [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

# OTTPlay für Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Architektur](docs/architecture.md) · [Sicherheit](SECURITY.md) · [Mitwirken](CONTRIBUTING.md)

Steuern Sie registrierte OTTPlay-Player aus Home Assistant über Ihren bestehenden [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server). Eine Verbindung stellt für jeden Player eine `media_player`- und eine `remote`-Entität bereit. Der Fernseher stellt ausgehende Anfragen an den Controller; Home Assistant benötigt weder einen lauschenden Port am Fernseher noch einen MQTT-Broker oder einen zweiten Brückenprozess.

![Funktionsweise](docs/diagrams/architecture.svg)

## Funktionen

- Wiedergabestatus vom laufenden Player; nicht erreichbare Geräte werden klar gekennzeichnet.
- Wiedergabe/Pause, vorheriger/nächster Kanal, Positionswechsel und Lautstärke, soweit der Player dies unterstützt.
- Kanalwahl nach Nummer oder Name über `media_player.play_media`.
- Navigation über `remote.send_command`: Pfeile, OK, Zurück und weitere unterstützte Tasten.
- Einrichtung über die Oberfläche, Austausch der Zugangsdaten, englische/russische Oberflächentexte und bereinigte Diagnosedaten.
- Stabile Entitätskennungen, auch nach einem Neustart des Players.

Die Funktionen hängen von Player-Version, Wiedergabemodus und Verbindung ab. Stop- und Hardware-Ein/Aus-Tasten werden nicht angeboten: Standby/Aufwecken kann je nach Player etwas anderes bedeuten und ersetzt nicht das Stoppen/Fortsetzen der Wiedergabe. Die Integration erfindet weder den aktuellen Titel noch Bilder oder den Hardware-Einschaltzustand. Eine Controller-Bestätigung bedeutet, dass der Handler geantwortet hat; sie beweist weder ein sichtbares Bild noch hörbaren Ton. Der Zustand stammt aus einem nachfolgenden Lesevorgang.

## Installation

Erforderlich sind **Home Assistant 2026.10.0 oder neuer**, ein aktueller OTTPlay Control Server und ein Player mit Unterstützung für die Anfrage/Antwort-API. Dies ist eine benutzerdefinierte Integration, kein Bestandteil von Home Assistant Core und kein standardmäßig enthaltenes HACS-Repository.

**HACS:** Fügen Sie `ha-homelab/ha-ottplay` als benutzerdefiniertes Repository vom Typ **Integration** hinzu, installieren Sie **OTTPlay** und starten Sie Home Assistant neu. Aktivieren Sie in HACS Vorabversionen, wenn Sie eine Beta installieren.

**Manuell:** Laden Sie `ha-ottplay.zip` aus einem [Release](https://github.com/ha-homelab/ha-ottplay/releases), prüfen Sie die Prüfsumme und entpacken Sie dessen Verzeichnis `custom_components/ottplay` in Ihr HA-Konfigurationsverzeichnis. Bewahren Sie vorhandene HA-Dateien auf. Starten Sie Home Assistant neu.

Öffnen Sie **Settings → Devices & services → Add integration → OTTPlay**. Verwenden Sie eine URL, die Home Assistant selbst erreichen kann, einschließlich eines etwaigen Controller-Pfadpräfixes, zum Beispiel `https://controller.example.net/ott-control`.

Zwei Berechtigungsmodi werden unterstützt:

1. **Eingeschränkter Operator (empfohlen):** Verwenden Sie ein eigenes Token für Befehlsoperatoren und tragen Sie die erlaubten Player-IDs in das Konfigurationsformular ein. IDs erhalten Sie mit `ott devices`. Die Registrierung eines neuen Players erweitert diese Berechtigung nicht stillschweigend; aktualisieren Sie die Serverberechtigung und die Integrationskonfiguration bewusst.
2. **Automatisches Register:** Lassen Sie die Player-IDs leer und verwenden Sie das Server-Administratortoken. Die Integration liest das Serverregister und entdeckt neue Geräte. Diese Zugangsdaten gewähren deutlich umfassenderen Zugriff. Verwenden Sie sie nur mit einer vertrauenswürdigen HA-Instanz.

Gerätetokens und Operator-Tokens, die nur Diagnosen erlauben, sind hier ungeeignet. Siehe [Konfiguration und Berechtigungen](docs/configuration.md).

## Verwendung in Automationen

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

Ersetzen Sie die Beispiel-Entitätskennungen durch diejenigen Ihres Systems. Die Kanalwahl verwendet den aktuellen Anbieter des Players; sie lädt keine beliebige Medien-URL hoch. Die Konfiguration startet weder die Wiedergabe noch schaltet sie den Fernseher physisch ein oder aus.

## Entwicklung und Releases

Verwenden Sie Python 3.14 und `uv sync --locked`, danach `uv run pytest -q`, `uv run ruff check .` und `uv run ruff format --check .`. Die Tests prüfen Protokollfehler, Zugangsdaten, Lebenszyklus und tatsächliche HA-Entitätsdienste, ohne sich mit Geräten im Haushalt zu verbinden. Siehe [Release-Prozess](docs/releasing.md).

Die Einstellungen des öffentlichen Repositorys werden mit [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) verwaltet. CI verwendet festgeschriebene gemeinsame Workflows aus [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

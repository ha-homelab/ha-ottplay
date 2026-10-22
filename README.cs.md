# OTTPlay pro Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Architektura](docs/architecture.md) · [Zabezpečení](SECURITY.md) · [Přispívání](CONTRIBUTING.md)

Ovládejte registrované přehrávače OTTPlay z Home Assistant prostřednictvím svého stávajícího [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server). Jedno připojení poskytne každému přehrávači entitu `media_player` a entitu `remote`. Televizor odesílá požadavky řadiči; Home Assistant nepotřebuje naslouchající port na televizoru, broker MQTT ani další proces zprostředkovatele.

![Jak to funguje](docs/diagrams/architecture.svg)

## Co získáte

- Stav přehrávání načítaný z běžícího přehrávače s jasně označenými nedostupnými zařízeními.
- Přehrávání/pozastavení, předchozí/další kanál, posun v přehrávání a hlasitost, pokud je daný přehrávač podporuje.
- Výběr kanálu podle čísla nebo názvu přes `media_player.play_media`.
- Navigaci přes `remote.send_command`: šipky, OK, Zpět a další podporované klávesy.
- Konfiguraci v uživatelském rozhraní, výměnu přihlašovacích údajů, anglický/ruský překlad rozhraní a diagnostiku s odstraněnými citlivými údaji.
- Stálou identitu entit, a to i po restartu přehrávače.

Možnosti závisí na sestavení přehrávače, režimu přehrávání a připojení. Tlačítka zastavení a hardwarového napájení nejsou dostupná: pohotovostní režim a probuzení mohou mít u každého přehrávače jiný význam a nenahrazují zastavení ani obnovení přehrávání. Integrace si nevymýšlí aktuální název, obrázek ani stav napájení hardwaru. Potvrzení řadiče znamená, že obsluha odpověděla; nedokazuje, že je vidět obraz nebo slyšet zvuk. Stav se získává následným načtením.

## Instalace

Vyžaduje **Home Assistant 2026.10.0 nebo novější** a aktuální OTTPlay Control Server i přehrávač podporující API požadavek/odpověď. Jde o vlastní integraci, která není součástí Home Assistant Core ani výchozím repozitářem HACS.

**HACS:** přidejte `ha-homelab/ha-ottplay` jako vlastní repozitář typu **Integration**, nainstalujte **OTTPlay** a restartujte Home Assistant. Při instalaci beta verze povolte v HACS předběžná vydání.

**Ručně:** stáhněte `ha-ottplay.zip` z [vydání](https://github.com/ha-homelab/ha-ottplay/releases), ověřte kontrolní součet a rozbalte jeho adresář `custom_components/ottplay` do konfiguračního adresáře HA. Zachovejte stávající soubory HA. Restartujte Home Assistant.

Přejděte na **Nastavení → Zařízení a služby → Přidat integraci → OTTPlay**. Použijte URL dostupné přímo z Home Assistant, včetně případného prefixu cesty řadiče. Například `https://controller.example.net/ott-control`.

Podporovány jsou dva režimy autorizace:

1. **Operátor s omezenými právy (doporučeno):** použijte vyhrazený token operátora příkazů a do konfiguračního formuláře zadejte povolená ID přehrávačů. ID získáte příkazem `ott devices`. Registrace nového přehrávače toto oprávnění automaticky nerozšíří; oprávnění serveru a konfiguraci integrace aktualizujte záměrně.
2. **Automatický registr:** ponechte ID přehrávačů prázdná a použijte token správce serveru. Integrace načítá registr serveru a vyhledává nová zařízení. Tento přihlašovací údaj poskytuje podstatně širší přístup. Používejte jej pouze s důvěryhodnou instancí HA.

Tokeny zařízení ani tokeny operátora pouze pro diagnostiku zde nelze použít. Viz [konfigurace a oprávnění](docs/configuration.md).

## Použití v automatizaci

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

Ukázková ID entit nahraďte těmi, které byly vytvořeny ve vašem systému. Výběr kanálu používá aktuálního poskytovatele přehrávače; neposílá libovolnou URL média. Konfigurace nespouští přehrávání ani neovládá fyzické napájení televizoru.

## Vývoj a vydání

Použijte Python 3.14 a `uv sync --locked`, poté `uv run pytest -q`, `uv run ruff check .` a `uv run ruff format --check .`. Testy ověřují chyby protokolu, přihlašovací údaje, životní cyklus a skutečné služby entit HA bez připojení k domácím zařízením. Viz [proces vydávání](docs/releasing.md).

Nastavení veřejného repozitáře spravuje [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI používá sdílené workflow s pevně určenou revizí z [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

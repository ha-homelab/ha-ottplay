# OTTPlay per Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Architettura](docs/architecture.md) · [Sicurezza](SECURITY.md) · [Contribuire](CONTRIBUTING.md)

Controlla i lettori OTTPlay registrati da Home Assistant tramite il tuo [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) esistente. Una connessione offre a ogni lettore un'entità `media_player` e un'entità `remote`. Il televisore invia richieste al controller; Home Assistant non richiede una porta in ascolto sul televisore, un broker MQTT o un secondo processo bridge.

![Come funziona](docs/diagrams/architecture.svg)

## Funzionalità

- Stato di riproduzione letto dal lettore in esecuzione, con dispositivi non disponibili indicati chiaramente.
- Riproduzione/pausa, canale precedente/successivo, spostamento temporale e volume quando il lettore li supporta.
- Selezione del canale per numero o nome tramite `media_player.play_media`.
- Navigazione tramite `remote.send_command`: frecce, OK, Indietro e altri tasti supportati.
- Configurazione nell'interfaccia, sostituzione delle credenziali, traduzioni dell'interfaccia in inglese/russo e diagnostica senza dati sensibili.
- Identità stabili delle entità, anche dopo il riavvio del lettore.

Le capacità dipendono dalla versione del lettore, dalla modalità di riproduzione e dalla connessione. I pulsanti Stop e di alimentazione hardware non sono esposti: standby/risveglio possono avere significati diversi nei vari lettori e non sostituiscono l'arresto/la ripresa della riproduzione. L'integrazione non inventa il titolo corrente, le immagini o lo stato di alimentazione hardware. Una conferma del controller significa che il gestore ha risposto; non dimostra che un'immagine sia visibile o che l'audio sia udibile. Lo stato proviene da una lettura successiva.

## Installazione

Richiede **Home Assistant 2026.10.0 o successivo**, un OTTPlay Control Server aggiornato e un lettore che supporti l'API richiesta/risposta. È un'integrazione personalizzata, non fa parte di Home Assistant Core e non è un repository HACS predefinito.

**HACS:** aggiungi `ha-homelab/ha-ottplay` come repository personalizzato di tipo **Integration**, installa **OTTPlay**, quindi riavvia Home Assistant. Abilita le versioni preliminari in HACS per installare una beta.

**Manuale:** scarica `ha-ottplay.zip` da una [release](https://github.com/ha-homelab/ha-ottplay/releases), verificane il checksum ed estrai la sua cartella `custom_components/ottplay` nella cartella di configurazione HA. Conserva i file HA esistenti. Riavvia Home Assistant.

Apri **Settings → Devices & services → Add integration → OTTPlay**. Usa un URL raggiungibile da Home Assistant stesso, includendo l'eventuale prefisso del percorso del controller; per esempio `https://controller.example.net/ott-control`.

Sono supportate due modalità di autorizzazione:

1. **Operatore limitato (consigliato):** usa un token dedicato per l'operatore di comandi ed elenca nel modulo di configurazione gli ID dei lettori consentiti. Ottieni gli ID con `ott devices`. La registrazione di un nuovo lettore non amplia implicitamente questa autorizzazione; aggiorna esplicitamente i permessi sul server e la configurazione dell'integrazione.
2. **Registro automatico:** lascia vuoti gli ID dei lettori e usa il token amministratore del server. L'integrazione legge il registro del server e scopre nuovi dispositivi. Questa credenziale concede un accesso molto più ampio. Usala solo con un'istanza HA affidabile.

Qui non si possono usare token dei dispositivi o token operatore destinati solo alla diagnostica. Vedi [configurazione e permessi](docs/configuration.md).

## Utilizzo in un'automazione

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

Sostituisci gli ID di entità degli esempi con quelli creati nel tuo sistema. La selezione del canale utilizza il fornitore corrente del lettore; non carica un URL multimediale arbitrario. La configurazione non avvia la riproduzione e non aziona l'alimentazione fisica del televisore.

## Sviluppo e release

Usa Python 3.14 e `uv sync --locked`, poi `uv run pytest -q`, `uv run ruff check .` e `uv run ruff format --check .`. I test verificano errori di protocollo, credenziali, ciclo di vita e servizi reali delle entità HA senza collegarsi ai dispositivi domestici. Vedi il [processo di rilascio](docs/releasing.md).

Le impostazioni del repository pubblico sono gestite con [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI usa workflow condivisi fissati a versioni precise da [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

# OTTPlay dla Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Architektura](docs/architecture.md) · [Bezpieczeństwo](SECURITY.md) · [Współtworzenie](CONTRIBUTING.md)

Steruj zarejestrowanymi odtwarzaczami OTTPlay z Home Assistant przez istniejący [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server). Jedno połączenie udostępnia dla każdego odtwarzacza encję `media_player` i encję `remote`. Telewizor wysyła żądania do kontrolera; Home Assistant nie potrzebuje portu nasłuchującego na telewizorze, brokera MQTT ani dodatkowego procesu pośredniczącego.

![Jak to działa](docs/diagrams/architecture.svg)

## Dostępne możliwości

- Stan odtwarzania odczytywany z działającego odtwarzacza, z wyraźnym oznaczeniem niedostępnych urządzeń.
- Odtwarzanie/pauza, poprzedni/następny kanał, przewijanie i głośność, jeżeli dany odtwarzacz je obsługuje.
- Wybór kanału według numeru lub nazwy przez `media_player.play_media`.
- Nawigacja przez `remote.send_command`: strzałki, OK, Wstecz i inne obsługiwane klawisze.
- Konfiguracja w interfejsie, wymiana danych uwierzytelniających, angielskie/rosyjskie tłumaczenia interfejsu i diagnostyka z ukrytymi danymi wrażliwymi.
- Stałe tożsamości encji, również po ponownym uruchomieniu odtwarzacza.

Możliwości zależą od kompilacji odtwarzacza, trybu odtwarzania i połączenia. Przyciski zatrzymania i fizycznego zasilania nie są udostępniane: tryb czuwania i wybudzanie mogą mieć różne znaczenie w poszczególnych odtwarzaczach i nie zastępują zatrzymania ani wznowienia odtwarzania. Integracja nie wymyśla bieżącego tytułu, grafiki ani stanu zasilania sprzętu. Potwierdzenie kontrolera oznacza, że procedura obsługi odpowiedziała; nie dowodzi, że obraz jest widoczny lub dźwięk słyszalny. Stan pochodzi z kolejnego odczytu.

## Instalacja

Wymagane są **Home Assistant 2026.10.0 lub nowszy** oraz aktualny OTTPlay Control Server i odtwarzacz obsługujący API żądanie/odpowiedź. Jest to integracja niestandardowa, niebędąca częścią Home Assistant Core ani domyślnym repozytorium HACS.

**HACS:** dodaj `ha-homelab/ha-ottplay` jako niestandardowe repozytorium typu **Integration**, zainstaluj **OTTPlay**, a następnie uruchom ponownie Home Assistant. Instalując wersję beta, włącz wydania wstępne w HACS.

**Ręcznie:** pobierz `ha-ottplay.zip` z [wydania](https://github.com/ha-homelab/ha-ottplay/releases), sprawdź sumę kontrolną i wypakuj katalog `custom_components/ottplay` do katalogu konfiguracji HA. Zachowaj istniejące pliki HA. Uruchom ponownie Home Assistant.

Przejdź do **Ustawienia → Urządzenia i usługi → Dodaj integrację → OTTPlay**. Użyj adresu URL osiągalnego bezpośrednio z Home Assistant, uwzględniając prefiks ścieżki kontrolera, jeśli występuje. Na przykład `https://controller.example.net/ott-control`.

Obsługiwane są dwa tryby autoryzacji:

1. **Operator z ograniczonym dostępem (zalecane):** użyj dedykowanego tokenu operatora poleceń i wpisz do formularza konfiguracji dozwolone identyfikatory odtwarzaczy. Identyfikatory uzyskasz poleceniem `ott devices`. Rejestracja nowego odtwarzacza nie rozszerza automatycznie tego uprawnienia; świadomie zaktualizuj uprawnienia na serwerze i konfigurację integracji.
2. **Automatyczny rejestr:** pozostaw identyfikatory odtwarzaczy puste i użyj tokenu administratora serwera. Integracja odczytuje rejestr serwera i wykrywa nowe urządzenia. Ten token daje znacznie szerszy dostęp. Używaj go tylko z zaufaną instancją HA.

Nie można tu używać tokenów urządzeń ani tokenów operatora przeznaczonych wyłącznie do diagnostyki. Zobacz [konfigurację i uprawnienia](docs/configuration.md).

## Użycie w automatyzacji

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

Zastąp przykładowe identyfikatory encji identyfikatorami utworzonymi w swoim systemie. Wybór kanału korzysta z bieżącego dostawcy odtwarzacza; nie przesyła dowolnego adresu URL multimediów. Konfiguracja nie uruchamia odtwarzania ani nie steruje fizycznym zasilaniem telewizora.

## Rozwój i wydania

Użyj Python 3.14 oraz `uv sync --locked`, następnie `uv run pytest -q`, `uv run ruff check .` i `uv run ruff format --check .`. Testy sprawdzają błędy protokołu, dane uwierzytelniające, cykl życia i rzeczywiste usługi encji HA bez łączenia się z urządzeniami domowymi. Zobacz [proces wydawania](docs/releasing.md).

Ustawieniami publicznego repozytorium zarządza [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI korzysta ze współdzielonych workflow przypiętych do określonych rewizji z [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

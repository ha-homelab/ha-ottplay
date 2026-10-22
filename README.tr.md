# Home Assistant için OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Mimari](docs/architecture.md) · [Güvenlik](SECURITY.md) · [Katkıda bulunma](CONTRIBUTING.md)

Kayıtlı OTTPlay oynatıcılarını mevcut [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) üzerinden Home Assistant ile yönetin. Tek bir bağlantı, her oynatıcı için bir `media_player` ve bir `remote` varlığı sağlar. TV, denetleyiciye giden istekler gönderir; Home Assistant için TV'de dinleyen bir port, MQTT aracısı veya ikinci bir köprü süreci gerekmez.

![Nasıl çalışır](docs/diagrams/architecture.svg)

## Sunulan özellikler

- Çalışan oynatıcıdan okunan oynatma durumu ve erişilemeyen cihazların açıkça belirtilmesi.
- Oynatıcının desteklediği durumlarda oynatma/duraklatma, önceki/sonraki kanal, oynatma konumuna gitme ve ses düzeyi.
- `media_player.play_media` ile numara veya ada göre kanal seçimi.
- `remote.send_command` ile gezinme: oklar, OK, Geri ve desteklenen diğer tuşlar.
- Arayüzden yapılandırma, kimlik bilgilerinin değiştirilmesi, İngilizce/Rusça arayüz çevirileri ve hassas bilgileri gizlenmiş tanılama verileri.
- Oynatıcı yeniden başlatıldığında da korunan, sabit varlık kimlikleri.

Yetenekler oynatıcı derlemesine, oynatma moduna ve bağlantıya bağlıdır. Durdurma ve donanım güç düğmeleri sunulmaz: bekleme/uyandırma her oynatıcıda farklı anlamlara gelebilir ve oynatmayı durdurma/sürdürme yerine kullanılmaz. Entegrasyon mevcut başlığı, görseli veya donanımın güç durumunu uydurmaz. Denetleyici onayı, işleyicinin yanıt verdiği anlamına gelir; görüntünün göründüğünü veya sesin duyulduğunu kanıtlamaz. Durum, sonraki bir okumadan alınır.

## Kurulum

**Home Assistant 2026.10.0 veya üstü** ile istek/yanıt API'sini destekleyen güncel OTTPlay Control Server ve oynatıcı gerekir. Bu, özel bir entegrasyondur; Home Assistant Core'un parçası veya varsayılan bir HACS deposu değildir.

**HACS:** `ha-homelab/ha-ottplay` deposunu **Integration** türünde özel depo olarak ekleyin, **OTTPlay** uygulamasını kurun ve Home Assistant'ı yeniden başlatın. Beta kurarken HACS'te ön sürümleri etkinleştirin.

**Elle:** [Sürümlerden](https://github.com/ha-homelab/ha-ottplay/releases) `ha-ottplay.zip` dosyasını indirin, sağlama toplamını doğrulayın ve içindeki `custom_components/ottplay` dizinini HA yapılandırma dizininize çıkarın. Mevcut HA dosyalarını koruyun. Home Assistant'ı yeniden başlatın.

**Ayarlar → Cihazlar ve hizmetler → Entegrasyon ekle → OTTPlay** yolunu izleyin. Denetleyicinin varsa yol önekini de içeren, Home Assistant'ın kendisinin erişebileceği bir URL kullanın. Örneğin: `https://controller.example.net/ott-control`.

İki yetkilendirme modu desteklenir:

1. **Kısıtlı operatör (önerilir):** özel bir komut operatörü belirteci kullanın ve izin verilen oynatıcı kimliklerini yapılandırma formunda listeleyin. Kimlikleri `ott devices` ile alın. Yeni bir oynatıcı kaydetmek bu yetkiyi kendiliğinden genişletmez; sunucu yetkisini ve entegrasyon yapılandırmasını bilinçli olarak güncelleyin.
2. **Otomatik kayıt defteri:** oynatıcı kimliklerini boş bırakın ve sunucu yöneticisi belirtecini kullanın. Entegrasyon sunucunun kayıt defterini okur ve yeni cihazları keşfeder. Bu kimlik bilgisi çok daha geniş erişim sağlar. Yalnızca güvenilir bir HA örneğiyle kullanın.

Cihaz belirteçleri ve yalnızca tanılama amaçlı operatör belirteçleri burada kullanılamaz. [Yapılandırma ve izinlere](docs/configuration.md) bakın.

## Otomasyonda kullanım

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

Örnek varlık kimliklerini sisteminizde oluşturulanlarla değiştirin. Kanal seçimi oynatıcının mevcut sağlayıcısını kullanır; rastgele bir medya URL'si yüklemez. Yapılandırma oynatmayı başlatmaz veya TV'nin fiziksel gücünü yönetmez.

## Geliştirme ve sürümler

Python 3.14 kullanın; `uv sync --locked` ardından `uv run pytest -q`, `uv run ruff check .` ve `uv run ruff format --check .` çalıştırın. Testler evdeki cihazlara bağlanmadan protokol hatalarını, kimlik bilgilerini, yaşam döngüsünü ve gerçek HA varlık hizmetlerini sınar. [Sürüm sürecine](docs/releasing.md) bakın.

Herkese açık deponun ayarları [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) ile yönetilir. CI, [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) içindeki belirli revizyonlara sabitlenmiş ortak iş akışlarını kullanır.

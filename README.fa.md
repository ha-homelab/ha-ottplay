# OTTPlay برای Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[معماری](docs/architecture.md) · [امنیت](SECURITY.md) · [مشارکت](CONTRIBUTING.md)

پخش‌کننده‌های ثبت‌شدهٔ OTTPlay را از Home Assistant و از طریق [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) فعلی خود کنترل کنید. یک اتصال برای هر پخش‌کننده یک موجودیت `media_player` و یک موجودیت `remote` فراهم می‌کند. تلویزیون درخواست‌های خروجی را به کنترل‌کننده می‌فرستد؛ Home Assistant به درگاه شنونده روی تلویزیون، کارگزار MQTT یا یک فرایند پلِ دوم نیاز ندارد.

![نحوهٔ کار](docs/diagrams/architecture.svg)

## امکانات

- خواندن وضعیت پخش از پخش‌کنندهٔ در حال اجرا، با مشخص‌کردن واضح دستگاه‌های در دسترس‌نبودنی.
- پخش/مکث، کانال قبلی/بعدی، جابه‌جایی به موقعیت پخش و تنظیم صدا، در صورت پشتیبانی پخش‌کننده.
- انتخاب کانال بر اساس شماره یا نام از طریق `media_player.play_media`.
- پیمایش با `remote.send_command`: کلیدهای جهت، OK، بازگشت و دیگر کلیدهای پشتیبانی‌شده.
- پیکربندی از رابط کاربری، جایگزینی اطلاعات احراز هویت، ترجمهٔ انگلیسی/روسی رابط و داده‌های عیب‌یابی با اطلاعات حساس پوشانده‌شده.
- شناسه‌های پایدار موجودیت‌ها، حتی پس از راه‌اندازی مجدد پخش‌کننده.

قابلیت‌ها به نسخهٔ ساخت پخش‌کننده، حالت پخش و اتصال بستگی دارند. دکمه‌های توقف و برق سخت‌افزار ارائه نمی‌شوند: آماده‌به‌کار/بیدارشدن ممکن است در هر پخش‌کننده معنای متفاوتی داشته باشد و جایگزین توقف/ادامهٔ پخش نمی‌شود. این یکپارچه‌سازی عنوان فعلی، تصویر یا وضعیت برق سخت‌افزار را از خود نمی‌سازد. تأیید کنترل‌کننده یعنی پردازشگر درخواست پاسخ داده است؛ این تأیید ثابت نمی‌کند تصویر دیده یا صدا شنیده می‌شود. وضعیت از خواندن بعدی به دست می‌آید.

## نصب

به **Home Assistant 2026.10.0 یا جدیدتر**، و OTTPlay Control Server و پخش‌کنندهٔ به‌روز با پشتیبانی از API درخواست/پاسخ نیاز است. این یک یکپارچه‌سازی سفارشی است؛ بخشی از Home Assistant Core یا مخزن پیش‌فرض HACS نیست.

**HACS:** مخزن `ha-homelab/ha-ottplay` را به‌عنوان مخزن سفارشی از نوع **Integration** اضافه کنید، **OTTPlay** را نصب کنید و سپس Home Assistant را دوباره راه‌اندازی کنید. برای نصب نسخهٔ بتا، پیش‌انتشارها را در HACS فعال کنید.

**دستی:** فایل `ha-ottplay.zip` را از [یک انتشار](https://github.com/ha-homelab/ha-ottplay/releases) دریافت کنید، جمع کنترلی آن را بررسی کنید و پوشهٔ `custom_components/ottplay` داخل آن را در پوشهٔ پیکربندی HA استخراج کنید. فایل‌های فعلی HA را نگه دارید. Home Assistant را دوباره راه‌اندازی کنید.

به **تنظیمات → دستگاه‌ها و سرویس‌ها → افزودن یکپارچه‌سازی → OTTPlay** بروید. از URLای استفاده کنید که خود Home Assistant بتواند به آن دسترسی داشته باشد؛ هر پیشوند مسیر کنترل‌کننده را نیز در آن بیاورید. برای مثال: `https://controller.example.net/ott-control`.

دو حالت مجوزدهی پشتیبانی می‌شود:

1. **اپراتور محدود (پیشنهادی):** از توکن اختصاصی اپراتور فرمان استفاده کنید و شناسه‌های پخش‌کنندهٔ مجاز آن را در فرم پیکربندی وارد کنید. شناسه‌ها را با `ott devices` دریافت کنید. ثبت پخش‌کنندهٔ جدید این مجوز را خودکار گسترش نمی‌دهد؛ مجوز سرور و پیکربندی یکپارچه‌سازی را آگاهانه به‌روز کنید.
2. **فهرست ثبت خودکار:** شناسه‌های پخش‌کننده را خالی بگذارید و از توکن مدیر سرور استفاده کنید. یکپارچه‌سازی فهرست ثبت سرور را می‌خواند و دستگاه‌های جدید را پیدا می‌کند. این اطلاعات احراز هویت دسترسی بسیار گسترده‌تری می‌دهند. فقط با نمونهٔ قابل‌اعتماد HA از آن استفاده کنید.

توکن‌های دستگاه و توکن‌های اپراتور مخصوص عیب‌یابی در اینجا قابل استفاده نیستند. [پیکربندی و مجوزها](docs/configuration.md) را ببینید.

## استفاده در خودکارسازی

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

شناسه‌های موجودیت در مثال را با شناسه‌های ساخته‌شده در سیستم خود جایگزین کنید. انتخاب کانال از ارائه‌دهندهٔ فعلی پخش‌کننده استفاده می‌کند؛ URL دلخواه رسانه را بارگذاری نمی‌کند. پیکربندی نه پخش را آغاز می‌کند و نه برق فیزیکی تلویزیون را کنترل می‌کند.

## توسعه و انتشار

از Python 3.14 استفاده کنید و `uv sync --locked` را اجرا کنید، سپس `uv run pytest -q`، `uv run ruff check .` و `uv run ruff format --check .` را اجرا کنید. آزمون‌ها خطاهای پروتکل، اطلاعات احراز هویت، چرخهٔ عمر و سرویس‌های واقعی موجودیت‌های HA را بدون اتصال به دستگاه‌های خانه بررسی می‌کنند. [فرایند انتشار](docs/releasing.md) را ببینید.

تنظیمات مخزن عمومی با [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) مدیریت می‌شوند. CI از گردش‌کارهای مشترک [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) استفاده می‌کند که به بازبینی‌های مشخص ثابت شده‌اند.

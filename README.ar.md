# OTTPlay لـ Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[البنية](docs/architecture.md) · [الأمان](SECURITY.md) · [المساهمة](CONTRIBUTING.md)

تحكّم في مشغّلات OTTPlay المسجّلة من Home Assistant عبر [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) الذي تستخدمه حاليًا. يوفّر اتصال واحد كيان `media_player` وكيان `remote` لكل مشغّل. يرسل التلفاز طلبات صادرة إلى وحدة التحكّم؛ ولا يحتاج Home Assistant إلى منفذ يستقبل الاتصالات على التلفاز، أو وسيط MQTT، أو عملية جسر ثانية.

![آلية العمل](docs/diagrams/architecture.svg)

## الميزات المتاحة

- قراءة حالة التشغيل من المشغّل قيد التشغيل، مع تمييز الأجهزة غير المتاحة بوضوح.
- التشغيل والإيقاف المؤقت، والقناة السابقة والتالية، والانتقال إلى موضع في التشغيل، والتحكّم بمستوى الصوت، عندما يدعم المشغّل ذلك.
- اختيار القناة برقمها أو اسمها عبر `media_player.play_media`.
- التنقّل عبر `remote.send_command`: الأسهم وOK والرجوع وغيرها من المفاتيح المدعومة.
- الإعداد من واجهة المستخدم، واستبدال بيانات الاعتماد، وترجمة الواجهة إلى الإنجليزية والروسية، وبيانات تشخيص حُجبت منها المعلومات الحساسة.
- هويات ثابتة للكيانات، حتى بعد إعادة تشغيل المشغّل.

تعتمد الإمكانات على بنية المشغّل ووضع التشغيل والاتصال. لا تُتاح أزرار إيقاف التشغيل أو طاقة العتاد: فقد يختلف معنى الاستعداد والإيقاظ بين المشغّلات، ولا يُستخدمان بديلًا عن إيقاف تشغيل الوسائط واستئنافه. لا يختلق التكامل عنوانًا حاليًا أو صورة غلاف أو حالة لطاقة العتاد. يعني تأكيد وحدة التحكّم أن معالج الطلب قد ردّ؛ ولا يثبت أن الصورة ظاهرة أو الصوت مسموع. تُستمد الحالة من قراءة لاحقة.

## التثبيت

يتطلّب **Home Assistant 2026.10.0 أو أحدث**، وإصدارًا حديثًا من OTTPlay Control Server ومشغّلًا يدعم واجهة API للطلب والاستجابة. هذا تكامل مخصّص، وليس جزءًا من Home Assistant Core ولا مستودعًا افتراضيًا في HACS.

**HACS:** أضف `ha-homelab/ha-ottplay` كمستودع مخصّص من النوع **Integration**، وثبّت **OTTPlay**، ثم أعد تشغيل Home Assistant. فعّل الإصدارات الأولية في HACS عند تثبيت نسخة بيتا.

**يدويًا:** نزّل `ha-ottplay.zip` من [أحد الإصدارات](https://github.com/ha-homelab/ha-ottplay/releases)، وتحقّق من مجموع التحقّق، ثم استخرج مجلّد `custom_components/ottplay` الموجود فيه إلى مجلّد إعدادات HA. احتفظ بملفات HA الحالية. أعد تشغيل Home Assistant.

انتقل إلى **الإعدادات → الأجهزة والخدمات → إضافة تكامل → OTTPlay**. استخدم عنوان URL يستطيع Home Assistant نفسه الوصول إليه، مع تضمين أي بادئة لمسار وحدة التحكّم. مثلًا: `https://controller.example.net/ott-control`.

يتوفّر وضعان للتفويض:

1. **مشغّل بصلاحيات محدودة (موصى به):** استخدم رمزًا مخصّصًا لمشغّل الأوامر، وأدرج معرّفات المشغّلات المسموح له بها في نموذج الإعداد. احصل على المعرّفات عبر `ott devices`. لا يؤدي تسجيل مشغّل جديد إلى توسيع هذه الصلاحية تلقائيًا؛ حدّث صلاحيات الخادم وإعدادات التكامل بشكل صريح.
2. **سجل تلقائي:** اترك معرّفات المشغّلات فارغة واستخدم رمز مسؤول الخادم. يقرأ التكامل سجل الخادم ويكتشف الأجهزة الجديدة. تمنح بيانات الاعتماد هذه وصولًا أوسع بكثير. استخدمها فقط مع مثيل HA موثوق.

لا يمكن هنا استخدام رموز الأجهزة أو رموز المشغّل المخصّصة للتشخيص فقط. راجع [الإعداد والصلاحيات](docs/configuration.md).

## الاستخدام في الأتمتة

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

استبدل معرّفات الكيانات في الأمثلة بتلك التي أُنشئت في نظامك. يستخدم اختيار القناة مزوّد المشغّل الحالي؛ ولا يرفع عنوان URL عشوائيًا للوسائط. لا يبدأ الإعداد تشغيل الوسائط ولا يتحكّم في الطاقة الفعلية للتلفاز.

## التطوير والإصدارات

استخدم Python 3.14 ونفّذ `uv sync --locked`، ثم `uv run pytest -q` و`uv run ruff check .` و`uv run ruff format --check .`. تختبر الاختبارات أخطاء البروتوكول وبيانات الاعتماد ودورة الحياة وخدمات كيانات HA الفعلية دون الاتصال بالأجهزة المنزلية. راجع [عملية الإصدار](docs/releasing.md).

تُدار إعدادات المستودع العام عبر [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). يستخدم CI مسارات عمل مشتركة مثبّتة على مراجعات محدّدة من [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

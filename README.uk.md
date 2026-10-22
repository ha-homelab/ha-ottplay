# OTTPlay для Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Архітектура](docs/architecture.md) · [Безпека](SECURITY.md) · [Участь у розробці](CONTRIBUTING.md)

Керуйте зареєстрованими програвачами OTTPlay з Home Assistant через наявний [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server). Одне з'єднання надає кожному програвачу сутності `media_player` і `remote`. Телевізор надсилає вихідні запити до контролера; Home Assistant не потребує порту прослуховування на телевізорі, брокера MQTT чи другого процесу-посередника.

![Як це працює](docs/diagrams/architecture.svg)

## Можливості

- Стан відтворення, зчитаний із запущеного програвача, з чітким позначенням недоступних пристроїв.
- Відтворення/пауза, попередній/наступний канал, перемотування та гучність, якщо програвач їх підтримує.
- Вибір каналу за номером або назвою через `media_player.play_media`.
- Навігація через `remote.send_command`: стрілки, OK, Назад та інші підтримувані клавіші.
- Налаштування через інтерфейс, заміна облікових даних, англійська/російська локалізація інтерфейсу та діагностика з прихованими конфіденційними даними.
- Стабільні ідентифікатори сутностей, зокрема після перезапуску програвача.

Можливості залежать від збірки програвача, режиму відтворення та з'єднання. Кнопки зупинки й апаратного живлення не надаються: очікування та пробудження можуть мати різне значення для різних програвачів і не підміняють зупинку чи поновлення відтворення. Інтеграція не вигадує поточну назву, обкладинку чи стан живлення обладнання. Підтвердження контролера означає, що обробник відповів; це не доводить, що зображення видно або звук чутно. Стан надходить під час наступного зчитування.

## Встановлення

Потрібні **Home Assistant 2026.10.0 або новіший**, а також актуальні OTTPlay Control Server і програвач із підтримкою API запит/відповідь. Це користувацька інтеграція, яка не входить до Home Assistant Core і не є типовим репозиторієм HACS.

**HACS:** додайте `ha-homelab/ha-ottplay` як користувацький репозиторій типу **Integration**, установіть **OTTPlay**, а потім перезапустіть Home Assistant. Для встановлення бета-версії ввімкніть попередні випуски в HACS.

**Вручну:** завантажте `ha-ottplay.zip` із [випуску](https://github.com/ha-homelab/ha-ottplay/releases), перевірте контрольну суму та розпакуйте каталог `custom_components/ottplay` у каталог конфігурації HA. Збережіть наявні файли HA. Перезапустіть Home Assistant.

Відкрийте **Налаштування → Пристрої та служби → Додати інтеграцію → OTTPlay**. Використовуйте URL, доступний самому Home Assistant, включно з префіксом шляху контролера, якщо він є. Наприклад, `https://controller.example.net/ott-control`.

Підтримуються два режими авторизації:

1. **Оператор з обмеженими правами (рекомендовано):** використовуйте окремий токен оператора команд і вкажіть дозволені ідентифікатори програвачів у формі налаштування. Отримайте ідентифікатори командою `ott devices`. Реєстрація нового програвача не розширює цей дозвіл автоматично; свідомо оновлюйте права на сервері та налаштування інтеграції.
2. **Автоматичний реєстр:** залиште ідентифікатори програвачів порожніми та використовуйте токен адміністратора сервера. Інтеграція читає реєстр сервера й виявляє нові пристрої. Ці облікові дані надають значно ширший доступ. Використовуйте їх лише з довіреним екземпляром HA.

Токени пристроїв і токени оператора лише для діагностики тут непридатні. Дивіться [налаштування та дозволи](docs/configuration.md).

## Використання в автоматизації

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

Замініть приклади ідентифікаторів сутностей на створені у вашій системі. Вибір каналу використовує поточного провайдера програвача; він не передає довільний URL медіа. Налаштування не запускає відтворення та не керує фізичним живленням телевізора.

## Розробка та випуски

Використовуйте Python 3.14 і `uv sync --locked`, потім `uv run pytest -q`, `uv run ruff check .` та `uv run ruff format --check .`. Тести перевіряють збої протоколу, облікові дані, життєвий цикл і справжні служби сутностей HA без підключення до домашніх пристроїв. Дивіться [процес випуску](docs/releasing.md).

Налаштування публічного репозиторію керуються через [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI використовує спільні робочі процеси, закріплені за конкретними ревізіями, з [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

# OTTPlay для Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[English](README.md) · [Архитектура](docs/architecture.md) · [Безопасность](SECURITY.md)

Интеграция подключает Home Assistant к существующему
[серверу управления OTTPlay](https://github.com/open-ott-play/ottplay-control-server).
Каждому плееру соответствуют `media_player` и пульт `remote`.
Телевизор сам обращается к серверу: отдельный порт на телевизоре, MQTT и ещё один
процесс моста не нужны.

![Схема работы](docs/diagrams/architecture.svg)

## Возможности

- Состояние воспроизведения из работающего плеера; отключённые устройства недоступны.
- Воспроизведение, пауза, предыдущий/следующий канал, перемотка и громкость —
  когда эти действия поддерживает конкретный плеер.
- Выбор канала по номеру или названию через `media_player.play_media`.
- Стрелки, OK, «Назад» и другие доступные кнопки через `remote.send_command`.
- Настройка через интерфейс HA, обновление учётных данных, русские и английские
  подписи, диагностический отчёт без секретов.

Кнопки Stop и питания не добавляются: ожидание и пробуждение могут вести себя
по-разному на разных плеерах и не подменяют остановку или продолжение видео.

Название текущего фильма, обложка и питание телевизора не выдумываются, если
сервер их не сообщает. Ответ обработчика не доказывает наличие изображения
или звука; состояние обновляется отдельным чтением.

## Установка

Нужны **Home Assistant 2026.10.0 или новее**, актуальные сервер управления и
плеер OTTPlay с API запросов и ответов. Это пользовательская интеграция;
она не входит в Home Assistant Core или стандартный список HACS.

В HACS добавьте `ha-homelab/ha-ottplay` как пользовательский репозиторий типа
**Integration**, установите **OTTPlay** и перезапустите HA. Для бета-версии
включите показ предварительных выпусков.

Для ручной установки скачайте `ha-ottplay.zip` из
[выпуска](https://github.com/ha-homelab/ha-ottplay/releases), проверьте контрольную
сумму и перенесите `custom_components/ottplay` в каталог конфигурации HA.
Существующие файлы HA сохраняются. Перезапустите Home Assistant.

Откройте **Настройки → Устройства и службы → Добавить интеграцию → OTTPlay**.
Адрес сервера должен быть доступен самому HA, включая префикс пути, если он есть.

Режимы доступа:

1. **Ограниченный оператор — рекомендуется.** Отдельный токен управления и
   список разрешённых ID плееров. ID можно получить командой `ott devices`.
   При добавлении нового плеера обновите разрешение на сервере и настройку HA.
2. **Автоматический реестр.** Оставьте список ID пустым и используйте
   административный токен сервера. Новые регистрации обнаруживаются автоматически,
   но этот токен даёт HA значительно более широкие права.

Токен отдельного плеера и токен только для диагностики не подходят.
Подробности: [настройка и права](docs/configuration.md).

## Автоматизация

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

Замените ID сущности на созданный в вашем HA. Канал выбирается в текущем
провайдере плеера. Произвольные URL видео не загружаются. Настройка интеграции
не запускает просмотр и не переключает физическое питание телевизора.

Разработка: Python 3.14, `uv sync --locked`, `uv run pytest -q`,
`uv run ruff check .`. [Процесс выпуска](docs/releasing.md).

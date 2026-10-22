# OTTPlay עבור Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[ארכיטקטורה](docs/architecture.md) · [אבטחה](SECURITY.md) · [תרומה לפרויקט](CONTRIBUTING.md)

שליטה בנגני OTTPlay רשומים מתוך Home Assistant באמצעות [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) הקיים שלכם. חיבור אחד מספק לכל נגן ישות `media_player` וישות `remote`. הטלוויזיה שולחת בקשות יוצאות לבקר; Home Assistant אינו זקוק לפורט מאזין בטלוויזיה, למתווך MQTT או לתהליך גישור נוסף.

![איך זה עובד](docs/diagrams/architecture.svg)

## היכולות הזמינות

- קריאת מצב הניגון מהנגן הפעיל, עם סימון ברור של מכשירים שאינם זמינים.
- ניגון/השהיה, ערוץ קודם/הבא, מעבר למיקום בניגון ועוצמת קול, כאשר הנגן תומך בכך.
- בחירת ערוץ לפי מספר או שם באמצעות `media_player.play_media`.
- ניווט באמצעות `remote.send_command`: חצים, OK, חזרה ומקשים נתמכים נוספים.
- הגדרה דרך ממשק המשתמש, החלפת פרטי גישה, תרגומי ממשק לאנגלית ולרוסית ונתוני אבחון שהמידע הרגיש הוסתר בהם.
- מזהים קבועים לישויות, גם לאחר הפעלה מחדש של הנגן.

היכולות תלויות בגרסת הבנייה של הנגן, במצב הניגון ובחיבור. לחצני עצירה ומתח של החומרה אינם חשופים: להמתנה ולהתעוררות עשויה להיות משמעות שונה בכל נגן, והן אינן משמשות תחליף לעצירת הניגון או לחידושו. האינטגרציה אינה ממציאה כותרת נוכחית, תמונה או מצב מתח של החומרה. אישור מהבקר אומר שמטפל הבקשה השיב; הוא אינו מוכיח שתמונה מוצגת או שקול נשמע. המצב מתקבל מקריאה עוקבת.

## התקנה

נדרשים **Home Assistant 2026.10.0 ומעלה** וכן OTTPlay Control Server ונגן עדכניים התומכים ב־API של בקשה/תגובה. זוהי אינטגרציה מותאמת אישית, שאינה חלק מ־Home Assistant Core ואינה מאגר ברירת מחדל של HACS.

**HACS:** הוסיפו את `ha-homelab/ha-ottplay` כמאגר מותאם אישית מסוג **Integration**, התקינו את **OTTPlay** והפעילו מחדש את Home Assistant. בעת התקנת גרסת בטא, הפעילו ב־HACS את האפשרות לגרסאות מוקדמות.

**ידנית:** הורידו את `ha-ottplay.zip` מתוך [גרסה שפורסמה](https://github.com/ha-homelab/ha-ottplay/releases), בדקו את סכום הביקורת שלו וחלצו את התיקייה `custom_components/ottplay` שבתוכו אל תיקיית התצורה של HA. שמרו את קובצי HA הקיימים. הפעילו מחדש את Home Assistant.

עברו אל **הגדרות → מכשירים ושירותים → הוספת אינטגרציה → OTTPlay**. השתמשו בכתובת URL ש־Home Assistant עצמו יכול להגיע אליה, כולל קידומת הנתיב של הבקר אם קיימת. לדוגמה: `https://controller.example.net/ott-control`.

נתמכים שני מצבי הרשאה:

1. **מפעיל מוגבל (מומלץ):** השתמשו בטוקן ייעודי למפעיל פקודות והזינו בטופס התצורה את מזהי הנגנים המותרים לו. את המזהים אפשר לקבל באמצעות `ott devices`. רישום נגן חדש אינו מרחיב הרשאה זו באופן אוטומטי; עדכנו במפורש את ההרשאה בשרת ואת תצורת האינטגרציה.
2. **מרשם אוטומטי:** השאירו את מזהי הנגנים ריקים והשתמשו בטוקן מנהל השרת. האינטגרציה קוראת את מרשם השרת ומגלה מכשירים חדשים. פרטי גישה אלה מעניקים גישה רחבה הרבה יותר. השתמשו בהם רק עם מופע HA מהימן.

אי אפשר להשתמש כאן בטוקנים של מכשירים או בטוקנים של מפעיל המיועדים לאבחון בלבד. ראו [תצורה והרשאות](docs/configuration.md).

## שימוש באוטומציה

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

החליפו את מזהי הישויות שבדוגמאות באלה שנוצרו במערכת שלכם. בחירת הערוץ משתמשת בספק הנוכחי של הנגן; היא אינה מעלה כתובת URL שרירותית של מדיה. ההגדרה אינה מתחילה ניגון ואינה מפעילה את אספקת המתח הפיזית של הטלוויזיה.

## פיתוח וגרסאות

השתמשו ב־Python 3.14 והפעילו `uv sync --locked`, ואחר כך `uv run pytest -q`,‏ `uv run ruff check .` ו־`uv run ruff format --check .`. הבדיקות בוחנות כשלי פרוטוקול, פרטי גישה, מחזור חיים ושירותים אמיתיים של ישויות HA, בלי להתחבר למכשירים בבית. ראו [תהליך פרסום הגרסאות](docs/releasing.md).

הגדרות המאגר הציבורי מנוהלות באמצעות [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). ה־CI משתמש בתהליכי עבודה משותפים מ־[venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit), המוצמדים לרוויזיות מסוימות.

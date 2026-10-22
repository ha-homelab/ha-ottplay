# OTTPlay สำหรับ Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[สถาปัตยกรรม](docs/architecture.md) · [ความปลอดภัย](SECURITY.md) · [การมีส่วนร่วม](CONTRIBUTING.md)

ควบคุมเครื่องเล่น OTTPlay ที่ลงทะเบียนไว้จาก Home Assistant ผ่าน [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) ที่คุณใช้อยู่ การเชื่อมต่อเดียวทำให้เครื่องเล่นแต่ละเครื่องมีเอนทิตี `media_player` และเอนทิตี `remote` ทีวีเป็นฝ่ายส่งคำขอออกไปยังตัวควบคุม Home Assistant จึงไม่ต้องใช้พอร์ตที่รอรับการเชื่อมต่อบนทีวี ตัวกลาง MQTT หรือโปรเซสบริดจ์ตัวที่สอง

![วิธีทำงาน](docs/diagrams/architecture.svg)

## ความสามารถที่มี

- อ่านสถานะการเล่นจากเครื่องเล่นที่กำลังทำงาน พร้อมระบุอุปกรณ์ที่ไม่พร้อมใช้งานอย่างชัดเจน
- เล่น/หยุดชั่วคราว ช่องก่อนหน้า/ถัดไป เลื่อนไปยังตำแหน่งการเล่น และปรับระดับเสียง หากเครื่องเล่นนั้นรองรับ
- เลือกช่องตามหมายเลขหรือชื่อผ่าน `media_player.play_media`
- นำทางผ่าน `remote.send_command`: ปุ่มลูกศร OK ย้อนกลับ และปุ่มอื่นที่รองรับ
- ตั้งค่าผ่าน UI เปลี่ยนข้อมูลรับรอง มีคำแปลอินเทอร์เฟซภาษาอังกฤษ/รัสเซีย และข้อมูลวินิจฉัยที่ปกปิดข้อมูลอ่อนไหวแล้ว
- ตัวระบุเอนทิตีคงเดิม แม้จะเริ่มเครื่องเล่นใหม่

ความสามารถขึ้นอยู่กับรุ่นบิลด์ของเครื่องเล่น โหมดการเล่น และการเชื่อมต่อ ไม่มีปุ่มหยุดและปุ่มเปิดปิดฮาร์ดแวร์ให้ใช้: สแตนด์บาย/ปลุกอาจมีความหมายต่างกันในแต่ละเครื่องเล่น จึงไม่ใช้แทนการหยุด/เล่นต่อ อินทิเกรชันจะไม่สร้างชื่อปัจจุบัน ภาพประกอบ หรือสถานะพลังงานของฮาร์ดแวร์ขึ้นเอง การตอบรับจากตัวควบคุมหมายความว่าตัวจัดการคำขอตอบกลับแล้ว ไม่ได้ยืนยันว่ามองเห็นภาพหรือได้ยินเสียง สถานะได้มาจากการอ่านครั้งถัดไป

## การติดตั้ง

ต้องใช้ **Home Assistant 2026.10.0 หรือใหม่กว่า** พร้อม OTTPlay Control Server และเครื่องเล่นรุ่นปัจจุบันที่รองรับ API แบบคำขอ/การตอบกลับ นี่คืออินทิเกรชันที่เพิ่มเอง ไม่ใช่ส่วนหนึ่งของ Home Assistant Core และไม่ใช่ที่เก็บเริ่มต้นของ HACS

**HACS:** เพิ่ม `ha-homelab/ha-ottplay` เป็นที่เก็บที่กำหนดเองชนิด **Integration** ติดตั้ง **OTTPlay** แล้วเริ่ม Home Assistant ใหม่ เมื่อติดตั้งเบตา ให้เปิดใช้รุ่นก่อนเผยแพร่ใน HACS

**ติดตั้งเอง:** ดาวน์โหลด `ha-ottplay.zip` จาก[รุ่นเผยแพร่](https://github.com/ha-homelab/ha-ottplay/releases) ตรวจสอบค่าเช็กซัม แล้วแตกไดเรกทอรี `custom_components/ottplay` ภายในไปยังไดเรกทอรีการตั้งค่า HA เก็บไฟล์ HA เดิมไว้ เริ่ม Home Assistant ใหม่

ไปที่ **การตั้งค่า → อุปกรณ์และบริการ → เพิ่มอินทิเกรชัน → OTTPlay** ใช้ URL ที่ Home Assistant เองเข้าถึงได้ โดยรวมคำนำหน้าเส้นทางของตัวควบคุมด้วยหากมี เช่น `https://controller.example.net/ott-control`

รองรับการให้สิทธิ์สองโหมด:

1. **ผู้ปฏิบัติงานแบบจำกัดสิทธิ์ (แนะนำ):** ใช้โทเคนเฉพาะสำหรับผู้ปฏิบัติงานคำสั่ง และระบุ ID เครื่องเล่นที่โทเคนนั้นได้รับอนุญาตในแบบฟอร์มการตั้งค่า ดู ID ได้จาก `ott devices` การลงทะเบียนเครื่องเล่นใหม่ไม่ได้ขยายสิทธิ์นี้โดยอัตโนมัติ ให้ปรับสิทธิ์บนเซิร์ฟเวอร์และการตั้งค่าอินทิเกรชันอย่างชัดเจนเมื่อจำเป็น
2. **ทะเบียนอัตโนมัติ:** เว้น ID เครื่องเล่นว่างไว้และใช้โทเคนผู้ดูแลเซิร์ฟเวอร์ อินทิเกรชันจะอ่านทะเบียนของเซิร์ฟเวอร์และค้นพบอุปกรณ์ใหม่ ข้อมูลรับรองนี้ให้สิทธิ์เข้าถึงกว้างกว่ามาก ใช้กับอินสแตนซ์ HA ที่เชื่อถือได้เท่านั้น

ไม่สามารถใช้โทเคนอุปกรณ์หรือโทเคนผู้ปฏิบัติงานสำหรับวินิจฉัยเท่านั้นในส่วนนี้ ดู[การตั้งค่าและสิทธิ์](docs/configuration.md)

## ใช้ในระบบอัตโนมัติ

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

แทนที่ ID เอนทิตีในตัวอย่างด้วย ID ที่สร้างในระบบของคุณ การเลือกช่องใช้ผู้ให้บริการปัจจุบันของเครื่องเล่น ไม่ได้อัปโหลด URL สื่อใด ๆ ตามใจชอบ การตั้งค่าไม่เริ่มเล่นสื่อและไม่ควบคุมการจ่ายไฟจริงของทีวี

## การพัฒนาและการเผยแพร่

ใช้ Python 3.14 และรัน `uv sync --locked` ตามด้วย `uv run pytest -q`, `uv run ruff check .` และ `uv run ruff format --check .` การทดสอบครอบคลุมความล้มเหลวของโปรโตคอล ข้อมูลรับรอง วงจรชีวิต และบริการเอนทิตี HA จริง โดยไม่เชื่อมต่ออุปกรณ์ภายในบ้าน ดู[กระบวนการเผยแพร่](docs/releasing.md)

การตั้งค่าที่เก็บสาธารณะจัดการผ่าน [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) ส่วน CI ใช้เวิร์กโฟลว์ร่วมจาก [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) ที่ตรึงไว้กับรีวิชันที่ระบุ

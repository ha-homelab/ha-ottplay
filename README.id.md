# OTTPlay untuk Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Arsitektur](docs/architecture.md) · [Keamanan](SECURITY.md) · [Berkontribusi](CONTRIBUTING.md)

Kendalikan pemutar OTTPlay yang terdaftar dari Home Assistant melalui [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) yang sudah Anda gunakan. Satu koneksi menyediakan entitas `media_player` dan entitas `remote` untuk setiap pemutar. TV mengirim permintaan keluar ke pengontrol; Home Assistant tidak memerlukan porta yang mendengarkan koneksi di TV, broker MQTT, atau proses penghubung kedua.

![Cara kerjanya](docs/diagrams/architecture.svg)

## Fitur yang tersedia

- Status pemutaran dibaca dari pemutar yang berjalan, dengan perangkat yang tidak tersedia ditandai secara jelas.
- Putar/jeda, saluran sebelumnya/berikutnya, pencarian posisi pemutaran, dan volume jika didukung pemutar tersebut.
- Pemilihan saluran berdasarkan nomor atau nama melalui `media_player.play_media`.
- Navigasi melalui `remote.send_command`: tombol arah, OK, Kembali, dan tombol lain yang didukung.
- Konfigurasi melalui UI, penggantian kredensial, terjemahan antarmuka bahasa Inggris/Rusia, dan diagnostik dengan informasi sensitif disamarkan.
- Identitas entitas yang tetap stabil, termasuk setelah pemutar dimulai ulang.

Kemampuan bergantung pada build pemutar, mode pemutaran, dan koneksi. Tombol berhenti dan daya perangkat keras tidak disediakan: siaga/bangun dapat memiliki makna berbeda pada setiap pemutar dan tidak digunakan sebagai pengganti penghentian/pelanjutan pemutaran. Integrasi tidak mengarang judul saat ini, gambar sampul, atau status daya perangkat keras. Konfirmasi pengontrol berarti penangan telah membalas; itu tidak membuktikan bahwa gambar terlihat atau suara terdengar. Status berasal dari pembacaan berikutnya.

## Instalasi

Memerlukan **Home Assistant 2026.10.0 atau lebih baru** serta OTTPlay Control Server dan pemutar terkini yang mendukung API permintaan/respons. Ini adalah integrasi kustom, bukan bagian dari Home Assistant Core dan bukan repositori bawaan HACS.

**HACS:** tambahkan `ha-homelab/ha-ottplay` sebagai repositori kustom dengan jenis **Integration**, instal **OTTPlay**, lalu mulai ulang Home Assistant. Aktifkan prarilis di HACS saat memasang versi beta.

**Manual:** unduh `ha-ottplay.zip` dari [rilis](https://github.com/ha-homelab/ha-ottplay/releases), verifikasi checksum-nya, lalu ekstrak direktori `custom_components/ottplay` di dalamnya ke direktori konfigurasi HA. Pertahankan berkas HA yang sudah ada. Mulai ulang Home Assistant.

Buka **Pengaturan → Perangkat & layanan → Tambahkan integrasi → OTTPlay**. Gunakan URL yang dapat dijangkau langsung oleh Home Assistant, termasuk awalan jalur pengontrol jika ada. Misalnya, `https://controller.example.net/ott-control`.

Ada dua mode otorisasi:

1. **Operator terbatas (disarankan):** gunakan token operator perintah khusus dan cantumkan ID pemutar yang diizinkannya pada formulir konfigurasi. Dapatkan ID dari `ott devices`. Mendaftarkan pemutar baru tidak otomatis memperluas izin ini; perbarui izin server dan konfigurasi integrasi secara sengaja.
2. **Registri otomatis:** biarkan ID pemutar kosong dan gunakan token administrator server. Integrasi membaca registri server dan menemukan perangkat baru. Kredensial ini memberikan akses yang jauh lebih luas. Gunakan hanya dengan instans HA yang tepercaya.

Token perangkat dan token operator khusus diagnostik tidak dapat digunakan di sini. Lihat [konfigurasi dan izin](docs/configuration.md).

## Penggunaan dalam otomatisasi

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

Ganti ID entitas contoh dengan ID yang dibuat di sistem Anda. Pemilihan saluran menggunakan penyedia pemutar saat ini; fitur ini tidak mengunggah sembarang URL media. Konfigurasi tidak memulai pemutaran atau mengoperasikan daya fisik TV.

## Pengembangan dan rilis

Gunakan Python 3.14 dan `uv sync --locked`, kemudian `uv run pytest -q`, `uv run ruff check .`, dan `uv run ruff format --check .`. Pengujian mencakup kegagalan protokol, kredensial, siklus hidup, dan layanan entitas HA yang sebenarnya tanpa menghubungi perangkat rumah tangga. Lihat [proses rilis](docs/releasing.md).

Pengaturan repositori publik dikelola melalui [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI menggunakan alur kerja bersama yang dikunci ke revisi tertentu dari [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

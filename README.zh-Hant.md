# 適用於 Home Assistant 的 OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[架構](docs/architecture.md) · [安全性](SECURITY.md) · [參與貢獻](CONTRIBUTING.md)

透過既有的 [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server)，從 Home Assistant 控制已註冊的 OTTPlay 播放器。單一連線即可為每個播放器提供一個 `media_player` 實體與一個 `remote` 實體。電視會主動向控制器發出請求；Home Assistant 不需要電視開放監聽連接埠，也不需要 MQTT 訊息代理或額外的橋接程序。

![運作方式](docs/diagrams/architecture.svg)

## 提供的功能

- 從執行中的播放器讀取播放狀態，並清楚標示無法使用的裝置。
- 在播放器支援的情況下，提供播放/暫停、上一/下一頻道、跳轉播放位置與音量控制。
- 透過 `media_player.play_media` 依編號或名稱選擇頻道。
- 透過 `remote.send_command` 使用方向鍵、OK、返回及其他支援的按鍵導覽。
- 支援介面設定、憑證更換、英文/俄文介面翻譯，以及隱去敏感資訊的診斷資料。
- 維持穩定的實體識別，播放器重新啟動後也不改變。

具體功能取決於播放器建置版本、播放模式與連線。不提供停止按鈕與硬體電源按鈕：待命/喚醒在不同播放器上可能具有不同意義，不能用來代替停止/恢復播放。整合不會臆造目前的標題、封面圖片或硬體電源狀態。控制器的確認回應僅表示處理常式已回覆，並不能證明畫面可見或聲音可聽。狀態來自後續讀取。

## 安裝

需要 **Home Assistant 2026.10.0 或更新版本**，以及支援請求/回應 API 的最新版 OTTPlay Control Server 與播放器。這是自訂整合，不屬於 Home Assistant Core，也不是 HACS 預設儲存庫。

**HACS：** 將 `ha-homelab/ha-ottplay` 新增為類型為 **Integration** 的自訂儲存庫，安裝 **OTTPlay**，然後重新啟動 Home Assistant。安裝測試版時，請在 HACS 中啟用預先發行版本。

**手動安裝：** 從[發行頁面](https://github.com/ha-homelab/ha-ottplay/releases)下載 `ha-ottplay.zip`，驗證校驗和，然後將其中的 `custom_components/ottplay` 目錄解壓縮至 HA 設定目錄。保留既有的 HA 檔案。重新啟動 Home Assistant。

前往 **設定 → 裝置與服務 → 新增整合 → OTTPlay**。使用 Home Assistant 本身可存取的 URL；若控制器有路徑前綴，也需包含在內。例如：`https://controller.example.net/ott-control`。

支援兩種授權模式：

1. **受限操作員（建議）：** 使用專用的命令操作員權杖，並在設定表單中列出該權杖允許存取的播放器 ID。透過 `ott devices` 取得 ID。註冊新播放器不會自動擴大授權範圍；請明確更新伺服器授權與整合設定。
2. **自動登錄表：** 將播放器 ID 留空，並使用伺服器管理員權杖。整合會讀取伺服器登錄表並探索新裝置。此憑證授予的存取權限廣泛得多。僅在可信任的 HA 執行個體中使用。

此處不能使用裝置權杖或僅限診斷的操作員權杖。請參閱[設定與權限](docs/configuration.md)。

## 在自動化中使用

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

將範例實體 ID 替換為您系統中建立的實體 ID。頻道選擇使用播放器目前的供應商；它不會上傳任意媒體 URL。設定不會開始播放，也不會操作電視的實體電源。

## 開發與發行

使用 Python 3.14，執行 `uv sync --locked`，接著執行 `uv run pytest -q`、`uv run ruff check .` 及 `uv run ruff format --check .`。測試涵蓋通訊協定故障、憑證、生命週期與實際的 HA 實體服務，無須連線至家中裝置。請參閱[發行流程](docs/releasing.md)。

公開儲存庫的設定由 [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) 管理。CI 使用 [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) 中固定至特定修訂版本的共用工作流程。

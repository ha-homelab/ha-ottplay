# 用于 Home Assistant 的 OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[架构](docs/architecture.md) · [安全](SECURITY.md) · [参与贡献](CONTRIBUTING.md)

通过现有的 [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server)，从 Home Assistant 控制已注册的 OTTPlay 播放器。一个连接即可为每个播放器提供一个 `media_player` 实体和一个 `remote` 实体。电视主动向控制器发出请求；Home Assistant 不需要电视开放监听端口，也不需要 MQTT 代理或额外的桥接进程。

![工作原理](docs/diagrams/architecture.svg)

## 提供的功能

- 从正在运行的播放器读取播放状态，并明确标记不可用的设备。
- 在播放器支持的情况下，提供播放/暂停、上一/下一频道、跳转播放位置及音量控制。
- 通过 `media_player.play_media` 按编号或名称选择频道。
- 通过 `remote.send_command` 使用方向键、OK、返回及其他受支持的按键导航。
- 支持界面配置、凭据更换、英语/俄语界面翻译，以及隐去敏感信息的诊断数据。
- 保持稳定的实体标识，播放器重启后也不改变。

具体功能取决于播放器构建版本、播放模式和连接。不提供停止按钮和硬件电源按钮：待机/唤醒在不同播放器上可能有不同含义，不能用来代替停止/恢复播放。集成不会编造当前标题、封面图片或硬件电源状态。控制器的确认响应仅表示处理程序已回复，并不能证明画面可见或声音可听。状态来自后续读取。

## 安装

需要 **Home Assistant 2026.10.0 或更高版本**，以及支持请求/响应 API 的最新版 OTTPlay Control Server 和播放器。这是自定义集成，不属于 Home Assistant Core，也不是 HACS 默认仓库。

**HACS：** 将 `ha-homelab/ha-ottplay` 添加为类型为 **Integration** 的自定义仓库，安装 **OTTPlay**，然后重启 Home Assistant。安装测试版时，请在 HACS 中启用预发布版本。

**手动安装：** 从[发布页面](https://github.com/ha-homelab/ha-ottplay/releases)下载 `ha-ottplay.zip`，验证校验和，然后将其中的 `custom_components/ottplay` 目录解压到 HA 配置目录中。保留现有的 HA 文件。重启 Home Assistant。

前往 **设置 → 设备与服务 → 添加集成 → OTTPlay**。使用 Home Assistant 自身能够访问的 URL；如果控制器有路径前缀，也需包含在内。例如：`https://controller.example.net/ott-control`。

支持两种授权模式：

1. **受限操作员（推荐）：** 使用专用的命令操作员令牌，并在配置表单中列出该令牌允许访问的播放器 ID。通过 `ott devices` 获取 ID。注册新播放器不会自动扩大授权范围；请明确更新服务器授权和集成配置。
2. **自动注册表：** 将播放器 ID 留空，并使用服务器管理员令牌。集成读取服务器注册表并发现新设备。此凭据授予的访问权限广泛得多。仅在可信的 HA 实例中使用。

此处不能使用设备令牌或仅限诊断的操作员令牌。参见[配置与权限](docs/configuration.md)。

## 在自动化中使用

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

将示例实体 ID 替换为您的系统中创建的实体 ID。频道选择使用播放器当前的提供商；它不会上传任意媒体 URL。配置不会启动播放，也不会操作电视的物理电源。

## 开发与发布

使用 Python 3.14，运行 `uv sync --locked`，然后运行 `uv run pytest -q`、`uv run ruff check .` 和 `uv run ruff format --check .`。测试覆盖协议故障、凭据、生命周期和实际的 HA 实体服务，无需连接家庭设备。参见[发布流程](docs/releasing.md)。

公开仓库的设置由 [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) 管理。CI 使用 [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) 中固定到特定修订版本的共享工作流。

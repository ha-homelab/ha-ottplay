# Home Assistant 用 OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[アーキテクチャ](docs/architecture.md) · [セキュリティ](SECURITY.md) · [開発への参加](CONTRIBUTING.md)

既存の [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) を通じて、登録済みの OTTPlay プレーヤーを Home Assistant から操作できます。1 つの接続で、各プレーヤーに `media_player` エンティティと `remote` エンティティが提供されます。テレビからコントローラーへリクエストを送信するため、Home Assistant のためにテレビ側でポートを開いたり、MQTT ブローカーや別のブリッジプロセスを用意したりする必要はありません。

![仕組み](docs/diagrams/architecture.svg)

## 利用できる機能

- 動作中のプレーヤーから再生状態を読み取り、利用できないデバイスを明示します。
- プレーヤーが対応している場合、再生・一時停止、前後のチャンネルへの切り替え、シーク、音量調節を行えます。
- `media_player.play_media` で番号または名前を指定してチャンネルを選択できます。
- `remote.send_command` で矢印、OK、戻るなど、対応するキー操作を送信できます。
- UI からの設定、認証情報の差し替え、英語・ロシア語の UI 翻訳、機密情報を除去した診断データに対応します。
- プレーヤーを再起動してもエンティティの識別情報は維持されます。

利用できる機能は、プレーヤーのビルド、再生モード、接続状態によって異なります。停止ボタンとハードウェアの電源ボタンは公開しません。スタンバイや復帰の意味はプレーヤーごとに異なり、再生の停止・再開の代わりにはしません。この統合は、現在のタイトル、アートワーク、ハードウェアの電源状態を推測して補いません。コントローラーからの応答確認はハンドラーが応答したことを意味し、映像が表示されていることや音声が聞こえることを保証しません。状態は、その後の読み取りで取得します。

## インストール

**Home Assistant 2026.10.0 以降**、およびリクエスト・レスポンス API に対応した最新の OTTPlay Control Server とプレーヤーが必要です。これはカスタム統合であり、Home Assistant Core の一部でも、HACS の既定リポジトリでもありません。

**HACS:** `ha-homelab/ha-ottplay` を種類 **Integration** のカスタムリポジトリとして追加し、**OTTPlay** をインストールしてから Home Assistant を再起動します。ベータ版をインストールする場合は、HACS でプレリリースを有効にしてください。

**手動:** [リリース](https://github.com/ha-homelab/ha-ottplay/releases) から `ha-ottplay.zip` をダウンロードし、チェックサムを検証したうえで、その中の `custom_components/ottplay` ディレクトリを HA の設定ディレクトリに展開します。既存の HA ファイルは残してください。Home Assistant を再起動します。

**設定 → デバイスとサービス → 統合を追加 → OTTPlay** を開きます。コントローラーのパスプレフィックスがあればそれも含め、Home Assistant 自体から到達できる URL を指定します。例: `https://controller.example.net/ott-control`。

次の 2 つの認可モードに対応しています。

1. **制限付きオペレーター（推奨）:** コマンドオペレーター専用のトークンを使用し、そのトークンで許可されたプレーヤー ID を設定フォームに記入します。ID は `ott devices` で取得できます。新しいプレーヤーを登録しても、この権限が自動的に拡大されることはありません。必要に応じてサーバー側の許可と統合の設定を明示的に更新してください。
2. **自動レジストリ:** プレーヤー ID を空欄にし、サーバー管理者のトークンを使用します。統合がサーバーのレジストリを読み、新しいデバイスを検出します。この認証情報は、はるかに広いアクセス権を与えます。信頼できる HA インスタンスでのみ使用してください。

デバイストークンと診断専用のオペレータートークンは、ここでは使用できません。[設定と権限](docs/configuration.md) を参照してください。

## オートメーションでの使用

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

例にあるエンティティ ID を、ご自身のシステムで作成されたものに置き換えてください。チャンネル選択にはプレーヤーで現在使用しているプロバイダーが使われ、任意のメディア URL をアップロードするものではありません。設定によって再生が開始されたり、テレビの物理的な電源が操作されたりすることはありません。

## 開発とリリース

Python 3.14 を使い、`uv sync --locked`、続いて `uv run pytest -q`、`uv run ruff check .`、`uv run ruff format --check .` を実行します。テストは家庭内のデバイスに接続せず、プロトコルの障害、認証情報、ライフサイクル、および実際の HA エンティティサービスを検証します。[リリース手順](docs/releasing.md) を参照してください。

公開リポジトリの設定は [Terraform](https://github.com/4alvit/terraform-github-ha-homelab) で管理します。CI は [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit) の特定リビジョンに固定された共有ワークフローを使用します。

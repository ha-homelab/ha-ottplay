# Home Assistant용 OTTPlay

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[아키텍처](docs/architecture.md) · [보안](SECURITY.md) · [기여 안내](CONTRIBUTING.md)

기존 [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server)를 통해 등록된 OTTPlay 플레이어를 Home Assistant에서 제어합니다. 연결 하나로 각 플레이어에 `media_player` 엔티티와 `remote` 엔티티가 제공됩니다. TV가 컨트롤러로 요청을 보내므로 Home Assistant를 위해 TV에 수신 포트를 열거나, MQTT 브로커 또는 별도의 브리지 프로세스를 둘 필요가 없습니다.

![작동 방식](docs/diagrams/architecture.svg)

## 제공 기능

- 실행 중인 플레이어에서 재생 상태를 읽고, 사용할 수 없는 기기를 명확히 표시합니다.
- 해당 플레이어가 지원하는 경우 재생/일시 정지, 이전/다음 채널, 탐색 및 음량 조절을 제공합니다.
- `media_player.play_media`를 통해 번호 또는 이름으로 채널을 선택합니다.
- `remote.send_command`로 방향키, OK, 뒤로 등 지원되는 키를 조작합니다.
- UI 설정, 자격 증명 교체, 영어/러시아어 UI 번역 및 민감한 정보를 가린 진단 데이터를 제공합니다.
- 플레이어를 다시 시작해도 엔티티 식별 정보가 유지됩니다.

사용 가능한 기능은 플레이어 빌드, 재생 모드 및 연결에 따라 달라집니다. 정지 및 하드웨어 전원 버튼은 제공하지 않습니다. 대기와 깨우기는 플레이어마다 의미가 다를 수 있으며 재생 정지/재개의 대용으로 사용하지 않습니다. 통합은 현재 제목, 이미지 또는 하드웨어 전원 상태를 임의로 만들어 내지 않습니다. 컨트롤러의 확인 응답은 처리기가 응답했다는 뜻이며, 화면에 영상이 보이거나 소리가 들린다는 증거는 아닙니다. 상태는 후속 읽기에서 가져옵니다.

## 설치

**Home Assistant 2026.10.0 이상**과 요청/응답 API를 지원하는 최신 OTTPlay Control Server 및 플레이어가 필요합니다. 이 통합은 사용자 지정 통합이며 Home Assistant Core의 일부도, 기본 HACS 저장소도 아닙니다.

**HACS:** `ha-homelab/ha-ottplay`를 유형이 **Integration**인 사용자 지정 저장소로 추가하고 **OTTPlay**를 설치한 다음 Home Assistant를 다시 시작합니다. 베타 버전을 설치할 때는 HACS에서 사전 릴리스를 활성화하세요.

**수동:** [릴리스](https://github.com/ha-homelab/ha-ottplay/releases)에서 `ha-ottplay.zip`을 다운로드하고 체크섬을 확인한 후, 그 안의 `custom_components/ottplay` 디렉터리를 HA 설정 디렉터리에 압축 해제합니다. 기존 HA 파일은 유지하세요. Home Assistant를 다시 시작합니다.

**설정 → 기기 및 서비스 → 통합 추가 → OTTPlay**로 이동합니다. 컨트롤러 경로 접두사가 있다면 이를 포함하여 Home Assistant 자체에서 접근할 수 있는 URL을 사용하세요. 예: `https://controller.example.net/ott-control`.

두 가지 권한 부여 모드를 지원합니다.

1. **제한된 운영자(권장):** 명령 운영자 전용 토큰을 사용하고, 이 토큰에 허용된 플레이어 ID를 설정 양식에 입력합니다. ID는 `ott devices`로 확인합니다. 새 플레이어를 등록해도 이 권한이 자동으로 확대되지 않습니다. 서버의 허용 범위와 통합 설정을 명시적으로 업데이트하세요.
2. **자동 레지스트리:** 플레이어 ID를 비워 두고 서버 관리자 토큰을 사용합니다. 통합이 서버 레지스트리를 읽고 새 기기를 검색합니다. 이 자격 증명은 훨씬 광범위한 접근 권한을 부여합니다. 신뢰할 수 있는 HA 인스턴스에서만 사용하세요.

기기 토큰과 진단 전용 운영자 토큰은 여기서 사용할 수 없습니다. [설정 및 권한](docs/configuration.md)을 참조하세요.

## 자동화에서 사용

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

예제의 엔티티 ID를 시스템에서 생성된 ID로 바꾸세요. 채널 선택에는 플레이어의 현재 제공업체가 사용되며, 임의의 미디어 URL을 업로드하지 않습니다. 설정은 재생을 시작하거나 TV의 물리적 전원을 조작하지 않습니다.

## 개발 및 릴리스

Python 3.14를 사용하여 `uv sync --locked`를 실행한 다음 `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`를 실행합니다. 테스트는 가정 내 기기에 연결하지 않고 프로토콜 오류, 자격 증명, 수명 주기 및 실제 HA 엔티티 서비스를 검증합니다. [릴리스 절차](docs/releasing.md)를 참조하세요.

공개 저장소 설정은 [Terraform](https://github.com/4alvit/terraform-github-ha-homelab)으로 관리합니다. CI는 [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit)의 특정 리비전에 고정된 공유 워크플로를 사용합니다.

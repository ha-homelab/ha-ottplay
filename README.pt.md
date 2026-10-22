# OTTPlay para Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Arquitetura](docs/architecture.md) · [Segurança](SECURITY.md) · [Contribuir](CONTRIBUTING.md)

Controle os reprodutores OTTPlay registrados no Home Assistant através do seu [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) existente. Uma conexão fornece a cada reprodutor uma entidade `media_player` e uma entidade `remote`. A TV envia solicitações ao controlador; o Home Assistant não precisa de uma porta de escuta na TV, de um broker MQTT ou de um segundo processo de ponte.

![Como funciona](docs/diagrams/architecture.svg)

## Recursos

- Estado da reprodução lido do reprodutor em execução, com indicação clara de dispositivos indisponíveis.
- Reproduzir/pausar, canal anterior/seguinte, busca temporal e volume quando o reprodutor oferece suporte.
- Seleção de canal pelo número ou nome através de `media_player.play_media`.
- Navegação através de `remote.send_command`: setas, OK, Voltar e outras teclas compatíveis.
- Configuração pela interface, substituição de credenciais, traduções da interface em inglês/russo e diagnósticos com dados sensíveis ocultados.
- Identidades estáveis das entidades, inclusive após reiniciar o reprodutor.

Os recursos dependem da versão do reprodutor, do modo de reprodução e da conexão. Os botões Stop e de alimentação física não são expostos: standby/despertar pode ter significados diferentes em cada reprodutor e não substitui parar/retomar a reprodução. A integração não inventa o título atual, imagens ou o estado de alimentação do hardware. Uma confirmação do controlador significa que o manipulador respondeu; não comprova que haja imagem visível ou som audível. O estado vem de uma leitura posterior.

## Instalação

Requer **Home Assistant 2026.10.0 ou posterior**, um OTTPlay Control Server atualizado e um reprodutor compatível com a API de solicitação/resposta. É uma integração personalizada, não faz parte do Home Assistant Core e não é um repositório padrão do HACS.

**HACS:** adicione `ha-homelab/ha-ottplay` como repositório personalizado do tipo **Integration**, instale **OTTPlay** e reinicie o Home Assistant. Ative versões preliminares no HACS ao instalar uma beta.

**Manual:** baixe `ha-ottplay.zip` de uma [versão publicada](https://github.com/ha-homelab/ha-ottplay/releases), verifique a soma de verificação e extraia seu diretório `custom_components/ottplay` no diretório de configuração do HA. Preserve os arquivos existentes do HA. Reinicie o Home Assistant.

Abra **Settings → Devices & services → Add integration → OTTPlay**. Use uma URL acessível pelo próprio Home Assistant, incluindo qualquer prefixo de caminho do controlador; por exemplo, `https://controller.example.net/ott-control`.

Há dois modos de autorização:

1. **Operador restrito (recomendado):** use um token dedicado de operador de comandos e liste os IDs dos reprodutores permitidos no formulário de configuração. Obtenha os IDs com `ott devices`. Registrar um novo reprodutor não amplia silenciosamente essa autorização; atualize deliberadamente a permissão no servidor e a configuração da integração.
2. **Registro automático:** deixe os IDs dos reprodutores vazios e use o token de administrador do servidor. A integração lê o registro do servidor e descobre novos dispositivos. Essa credencial concede acesso muito mais amplo. Use-a apenas com uma instância confiável do HA.

Tokens de dispositivos e tokens de operador exclusivos para diagnóstico não podem ser usados aqui. Consulte [configuração e permissões](docs/configuration.md).

## Uso em uma automação

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

Substitua os IDs de entidades dos exemplos pelos criados no seu sistema. A seleção de canal usa o provedor atual do reprodutor; ela não carrega uma URL de mídia arbitrária. A configuração não inicia a reprodução nem aciona a alimentação física da TV.

## Desenvolvimento e versões

Use Python 3.14 e `uv sync --locked`, depois `uv run pytest -q`, `uv run ruff check .` e `uv run ruff format --check .`. Os testes exercitam falhas de protocolo, credenciais, ciclo de vida e serviços reais de entidades HA sem conectar aos dispositivos domésticos. Consulte o [processo de lançamento](docs/releasing.md).

As configurações do repositório público são gerenciadas com [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI usa workflows compartilhados fixados de [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

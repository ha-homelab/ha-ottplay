# OTTPlay para Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Arquitectura](docs/architecture.md) · [Seguridad](SECURITY.md) · [Contribuir](CONTRIBUTING.md)

Controle reproductores OTTPlay registrados desde Home Assistant mediante su [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) existente. Una conexión proporciona a cada reproductor una entidad `media_player` y otra `remote`. El televisor realiza solicitudes salientes al controlador; Home Assistant no necesita un puerto de escucha en el televisor, un broker MQTT ni un segundo proceso puente.

![Cómo funciona](docs/diagrams/architecture.svg)

## Funciones

- Estado de reproducción leído del reproductor en ejecución, con los dispositivos no disponibles claramente señalados.
- Reproducir/pausar, canal anterior/siguiente, desplazamiento temporal y volumen cuando el reproductor los admite.
- Selección de canal por número o nombre mediante `media_player.play_media`.
- Navegación mediante `remote.send_command`: flechas, OK, Atrás y otras teclas compatibles.
- Configuración mediante la interfaz, sustitución de credenciales, traducciones de interfaz al inglés/ruso y diagnósticos con datos sensibles ocultos.
- Identidades de entidad estables, incluso después de reiniciar el reproductor.

Las funciones dependen de la versión del reproductor, el modo de reproducción y la conexión. No se exponen botones Stop ni de encendido físico: la suspensión y la reactivación pueden tener distintos significados según el reproductor y no sustituyen detener/reanudar la reproducción. La integración no inventa el título actual, las ilustraciones ni el estado de alimentación del equipo. Una confirmación del controlador significa que el manejador respondió; no demuestra que se vea una imagen o se oiga sonido. El estado procede de una lectura posterior.

## Instalación

Requiere **Home Assistant 2026.10.0 o posterior**, un OTTPlay Control Server actualizado y un reproductor compatible con la API de solicitud/respuesta. Es una integración personalizada, no forma parte de Home Assistant Core ni está en el catálogo predeterminado de HACS.

**HACS:** añada `ha-homelab/ha-ottplay` como repositorio personalizado de tipo **Integration**, instale **OTTPlay** y reinicie Home Assistant. Active las versiones preliminares en HACS para instalar una beta.

**Manual:** descargue `ha-ottplay.zip` de una [versión publicada](https://github.com/ha-homelab/ha-ottplay/releases), verifique su suma de comprobación y extraiga su directorio `custom_components/ottplay` en el directorio de configuración de HA. Conserve los archivos existentes de HA. Reinicie Home Assistant.

Vaya a **Settings → Devices & services → Add integration → OTTPlay**. Use una URL accesible desde el propio Home Assistant, incluido cualquier prefijo de ruta del controlador; por ejemplo, `https://controller.example.net/ott-control`.

Se admiten dos modos de autorización:

1. **Operador restringido (recomendado):** use un token específico de operador de comandos e indique sus IDs de reproductor permitidos en el formulario de configuración. Obtenga los IDs con `ott devices`. Registrar un reproductor nuevo no amplía silenciosamente este permiso; actualice deliberadamente la autorización del servidor y la configuración de la integración.
2. **Registro automático:** deje vacíos los IDs de reproductor y use el token de administrador del servidor. La integración lee el registro del servidor y descubre dispositivos nuevos. Esta credencial concede un acceso mucho más amplio. Úsela solo con una instancia de HA de confianza.

Aquí no sirven los tokens de dispositivo ni los tokens de operador limitados a diagnóstico. Consulte [configuración y permisos](docs/configuration.md).

## Uso en una automatización

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

Sustituya los IDs de entidad de ejemplo por los creados en su sistema. La selección de canal utiliza el proveedor actual del reproductor; no carga una URL multimedia arbitraria. La configuración no inicia la reproducción ni acciona la alimentación física del televisor.

## Desarrollo y versiones

Use Python 3.14 y `uv sync --locked`, después `uv run pytest -q`, `uv run ruff check .` y `uv run ruff format --check .`. Las pruebas ejercitan fallos de protocolo, credenciales, ciclo de vida y servicios reales de entidades HA sin conectarse a dispositivos del hogar. Consulte el [proceso de publicación](docs/releasing.md).

La configuración del repositorio público se gestiona con [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI utiliza flujos compartidos fijados a versiones concretas de [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

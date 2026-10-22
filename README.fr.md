# OTTPlay pour Home Assistant

<!-- language-navigation:start -->
<p dir="ltr">
<a href="README.md" lang="en" dir="ltr">English</a> · <a href="README.ar.md" lang="ar" dir="rtl">العربية</a> · <a href="README.bn.md" lang="bn" dir="ltr">বাংলা</a> · <a href="README.cs.md" lang="cs" dir="ltr">Čeština</a> · <a href="README.de.md" lang="de" dir="ltr">Deutsch</a> · <a href="README.es.md" lang="es" dir="ltr">Español</a> · <a href="README.fa.md" lang="fa" dir="rtl">فارسی</a> · <a href="README.fr.md" lang="fr" dir="ltr">Français</a><br>
<a href="README.he.md" lang="he" dir="rtl">עברית</a> · <a href="README.hi.md" lang="hi" dir="ltr">हिन्दी</a> · <a href="README.id.md" lang="id" dir="ltr">Bahasa Indonesia</a> · <a href="README.it.md" lang="it" dir="ltr">Italiano</a> · <a href="README.ja.md" lang="ja" dir="ltr">日本語</a> · <a href="README.ko.md" lang="ko" dir="ltr">한국어</a> · <a href="README.nl.md" lang="nl" dir="ltr">Nederlands</a> · <a href="README.pl.md" lang="pl" dir="ltr">Polski</a><br>
<a href="README.pt.md" lang="pt" dir="ltr">Português</a> · <a href="README.ru.md" lang="ru" dir="ltr">Русский</a> · <a href="README.th.md" lang="th" dir="ltr">ไทย</a> · <a href="README.tr.md" lang="tr" dir="ltr">Türkçe</a> · <a href="README.uk.md" lang="uk" dir="ltr">Українська</a> · <a href="README.vi.md" lang="vi" dir="ltr">Tiếng Việt</a> · <a href="README.zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> · <a href="README.zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

[![RC fuzzing](https://img.shields.io/badge/fuzzing-RC_only-0a9f8f)](docs/fuzzing.md)

[Architecture](docs/architecture.md) · [Sécurité](SECURITY.md) · [Contribuer](CONTRIBUTING.md)

Pilotez les lecteurs OTTPlay enregistrés depuis Home Assistant via votre [OTTPlay Control Server](https://github.com/open-ott-play/ottplay-control-server) existant. Une connexion fournit à chaque lecteur une entité `media_player` et une entité `remote`. Le téléviseur envoie des requêtes au contrôleur ; Home Assistant n'a besoin ni d'un port d'écoute sur le téléviseur, ni d'un courtier MQTT, ni d'un second processus de passerelle.

![Fonctionnement](docs/diagrams/architecture.svg)

## Fonctionnalités

- État de lecture récupéré sur le lecteur en fonctionnement, avec indication claire des appareils indisponibles.
- Lecture/pause, chaîne précédente/suivante, déplacement dans la lecture et volume si le lecteur les prend en charge.
- Sélection d'une chaîne par numéro ou nom via `media_player.play_media`.
- Navigation via `remote.send_command` : flèches, OK, Retour et autres touches prises en charge.
- Configuration dans l'interface, remplacement des identifiants, interface en anglais/russe et diagnostics expurgés des données sensibles.
- Identités d'entités stables, y compris après le redémarrage du lecteur.

Les possibilités dépendent de la version du lecteur, du mode de lecture et de la connexion. Les boutons Stop et d'alimentation matérielle ne sont pas exposés : veille/réveil peut avoir une signification différente selon le lecteur et ne remplace pas l'arrêt/la reprise de lecture. L'intégration n'invente ni le titre en cours, ni les illustrations, ni l'état d'alimentation du matériel. Un accusé de réception du contrôleur signifie que le gestionnaire a répondu ; il ne prouve ni qu'une image est visible ni qu'un son est audible. L'état provient d'une lecture ultérieure.

## Installation

Nécessite **Home Assistant 2026.10.0 ou ultérieur**, un OTTPlay Control Server à jour et un lecteur prenant en charge l'API requête/réponse. Il s'agit d'une intégration personnalisée, absente de Home Assistant Core et des dépôts HACS proposés par défaut.

**HACS :** ajoutez `ha-homelab/ha-ottplay` comme dépôt personnalisé de type **Integration**, installez **OTTPlay**, puis redémarrez Home Assistant. Activez les préversions dans HACS pour installer une bêta.

**Manuellement :** téléchargez `ha-ottplay.zip` depuis une [version publiée](https://github.com/ha-homelab/ha-ottplay/releases), vérifiez sa somme de contrôle et extrayez son dossier `custom_components/ottplay` dans le dossier de configuration de HA. Conservez les fichiers HA existants. Redémarrez Home Assistant.

Ouvrez **Settings → Devices & services → Add integration → OTTPlay**. Utilisez une URL accessible par Home Assistant lui-même, en incluant tout préfixe de chemin du contrôleur ; par exemple `https://controller.example.net/ott-control`.

Deux modes d'autorisation sont disponibles :

1. **Opérateur restreint (recommandé) :** utilisez un jeton dédié d'opérateur de commandes et indiquez les IDs de lecteurs autorisés dans le formulaire. Obtenez les IDs avec `ott devices`. Enregistrer un nouveau lecteur n'étend pas silencieusement cette autorisation ; mettez délibérément à jour les droits côté serveur et la configuration de l'intégration.
2. **Registre automatique :** laissez les IDs de lecteurs vides et utilisez le jeton administrateur du serveur. L'intégration lit le registre du serveur et découvre les nouveaux appareils. Ce jeton donne un accès beaucoup plus large. Ne l'utilisez qu'avec une instance HA de confiance.

Les jetons d'appareils et les jetons d'opérateurs réservés au diagnostic ne conviennent pas ici. Voir [configuration et autorisations](docs/configuration.md).

## Utilisation dans une automatisation

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

Remplacez les IDs d'entités d'exemple par ceux créés sur votre système. La sélection de chaîne utilise le fournisseur actuel du lecteur ; elle ne charge pas une URL multimédia arbitraire. La configuration ne démarre pas la lecture et n'actionne pas l'alimentation physique du téléviseur.

## Développement et versions

Utilisez Python 3.14 et `uv sync --locked`, puis `uv run pytest -q`, `uv run ruff check .` et `uv run ruff format --check .`. Les tests couvrent les erreurs de protocole, les identifiants, le cycle de vie et les vrais services d'entités HA sans se connecter aux appareils du foyer. Voir le [processus de publication](docs/releasing.md).

Les paramètres du dépôt public sont gérés avec [Terraform](https://github.com/4alvit/terraform-github-ha-homelab). CI utilise les workflows partagés épinglés de [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit).

# README translations

The README is available in the 24 languages listed in `languages.json`, matching
the [ha-homelab organization profile](https://github.com/ha-homelab). Every page
links directly to the other README translations. Arabic, Persian and Hebrew
links declare right-to-left text direction.

`README.md` is the source for documentation updates. The 22 translations added
in this expansion cover its complete introduction, capabilities, limitations,
installation instructions, authorization modes, automation examples and
development workflow. Existing English and Russian content is preserved.
Other guides keep their existing language coverage. Documentation translations
do not add languages to the integration's user interface.

When changing the source README, update its translations in the same change.
Keep code examples, identifiers, version requirements and URLs unchanged unless
the underlying instructions also change. Translate link labels, image alternative
text, explanatory prose and headings. Avoid replacing a guide with a summary.

Run this check from the repository root using Python 3:

```sh
python3 scripts/check_readme_translations.py
```

The script checks the language-file inventory, navigation attributes, matching
YAML examples, preserved commands and identifiers, section counts and local link
targets. It checks technical completeness of the 22 new translations against
English; the older Russian page retains its previous scope. These structural
checks do not replace reading the translations for accuracy and fluency.

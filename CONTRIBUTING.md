# Contributing

Use Python 3.14 and install the pinned environment with `uv sync --locked`.
Run `uv run pytest -q`, `uv run ruff check .`, and `uv run ruff format --check .`.
Keep network tests local and deterministic; never require a contributor's TV,
Home Assistant credentials or subscription.

Changes require a pull request, passing CI and review. Preserve stable entity
IDs, validate protocol data before using it, distinguish unknown from false,
and keep mutation requests at-most-once on transport failures. Add regression
tests at the boundary changed, including unload/cancellation when relevant.
Update both READMEs and English/Russian UI translations for user-visible changes.

Do not commit local configuration, tokens, IP inventories, `.storage`, screenshots
of account settings, or copied household playlists. Generic examples only.

See [architecture](docs/architecture.md), [configuration](docs/configuration.md)
and [release process](docs/releasing.md).

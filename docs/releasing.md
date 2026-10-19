# Validation and release process

The public repository is provisioned through `terraform-github-ha-homelab`, using
the same protected-main, review, Actions and immutable-tag policies as the
organization's other public adapters. Infrastructure changes have their own PR.
No state files or infrastructure credentials belong in this source repository.

Development uses the committed `uv.lock` and Python 3.14. CI runs the pinned shared
Python and security workflows, the real Home Assistant test suite, HACS validation
and Hassfest. Required checks are collected into a final gate that fails when a
required job fails or is skipped. A local passing test does not substitute for CI.

`.release-policy.json` is the source of the generated shared release machinery.
Its toolkit revision is pinned. The workflow builds a frozen version plan and
packs tracked integration inputs with fixed ZIP metadata, producing:

- `ottplay.zip`: component files at archive root, consumed by HACS.
- `ha-ottplay.zip`: `custom_components/ottplay/…`, for manual installation.
- `SHA256SUMS` and the shared release evidence/manifest.

Each release needs a `## [base-version]` section in `CHANGELOG.md` with substantive
`### Upgrade` and `### Security` guidance; the repository tests validate the
current notes through the actual release parser before publication.

Beta/RC packages carry the corresponding integration version. Stable publication
uses the shared verified promotion process. Never move a published tag or replace
an existing release with different bytes. An updated implementation requires a
new candidate/version and fresh checks.

For manual verification, download a release, verify checksums, inspect the ZIP
layout, then install only the component directory. Keep a private backup of any
previous version and its configuration. Restart HA, verify the config entry is
loaded, and inspect entities. Use only explicitly chosen playback controls for
live acceptance; restoring prior playback is part of that check.

Development tests use local HTTP fixtures and isolated HA instances. Successful
state/control verification is not proof of sound or picture on every TV model.

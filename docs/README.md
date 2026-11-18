# Documentation

The Home Assistant integration that drives OTTPlay playback, with the release
tooling, signing path and translation coverage that go with it.

## Use it

- [Configuration and permissions](configuration.md) — the controller URL and what the integration needs.
- [Architecture and tradeoffs](architecture.md) — the design the integration commits to and what it gives up.
- [README translations](translations.md) — the 24 languages listed in `languages.json`.

## Release operation

- [Validation and release process](releasing.md) — how the public repository is provisioned and released.
- [CI and release operations](release-workflow.md) — `.release-policy.json` and the required status.
- [Version plans and manifest synchronization](VERSIONING.md) — the versioning opt-in.
- [Qualified GitHub CLI for release operations](release-github-cli.md) — the pinned CLI and Go versions.
- [Patched release signer and verifier](release-signer.md) — why the signer binary is exported only after its contract job.
- [Verify a signed release](release-signatures.md) — checking a signed artefact.

## Evidence

- [Release-candidate fuzz testing](fuzzing.md) — the target's URL normalizer and numeric admission checks.
- [Fuzzing release candidates](rc-fuzzing.md) — the reusable bounded fuzz workflow.
- [Release read recovery and rerun validation](release-read-safety.md) — the two fixes carried from the shared toolkit.
- [Early final-build runner check](runner-preflight.md) — why the check runs before the final build.

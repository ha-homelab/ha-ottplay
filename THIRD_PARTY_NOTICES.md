# Third-party notices

`custom_components/ottplay/brand/icon.png` is the OTTPlay browser application icon
from [open-ott-play/ottplay-foss](https://github.com/open-ott-play/ottplay-foss),
`js/browser-app/icon-512.png`, distributed under its MIT license. The original
notice is preserved in `custom_components/ottplay/brand/LICENSE.ottplay-foss`.

The shared release tools in `scripts/`, workflow helpers and generated workflows
come from [venus-os-ci-toolkit](https://github.com/victron-venus/venus-os-ci-toolkit),
at the exact revision in `.release-policy.json`. Their headers and notices are
retained. Test dependencies and their license metadata are pinned in `uv.lock`;
Home Assistant's code is not bundled in the integration release.

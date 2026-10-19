# Security

Report vulnerabilities privately using this repository's
[security advisory form](https://github.com/ha-homelab/ha-ottplay/security/advisories/new).
Do not post credentials, household controller URLs, diagnostic archives or
provider subscriptions in public issues.

The supported line is 0.1.x. Install the newest patch in that line. Prereleases
are evaluation builds; passing CI is not a guarantee about physical devices.

Use HTTPS with normal certificate validation outside a trusted private network.
HTTP is available for a controlled local network. Redirects are not followed
with credentials. URLs containing credentials, fragments or query strings are
not accepted. Tokens belong in HA's credential form, never in the URL.

Prefer a dedicated command operator with explicit device/action grants.
Administrator discovery is optional and intentionally described as broad access.
HA stores integration credentials in its local configuration-entry storage;
protect its configuration directory and backups. Diagnostics must exclude
credentials, controller URLs, player IDs and raw server responses.

Commands are never automatically replayed after an uncertain timeout. A failed
response can mean that a command was already received. Read state before retrying.
The integration does not provide shell execution, screenshots, provider-secret
export, firmware updates, arbitrary media URLs or physical-device power control.

"""Configure a control server through Home Assistant's UI."""

import re
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_TOKEN, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import AuthError, OttplayClient, OttplayError, PlayerUnavailable
from .const import CONF_DEVICES, DEVICE_ID_PATTERN, DOMAIN, MAX_DEVICES

PASSWORD = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def parse_devices(value: str) -> list[str]:
    """Normalize optional explicit IDs without silently dropping invalid IDs."""
    if not value.strip():
        return []
    values = [item.strip() for item in value.split(",")]
    if len(values) > MAX_DEVICES or any(not re.fullmatch(DEVICE_ID_PATTERN, v) for v in values):
        raise ValueError("Invalid device IDs")
    if len(set(values)) != len(values):
        raise ValueError("Duplicate device IDs")
    return values


class OttplayConfigFlow(ConfigFlow, domain=DOMAIN):
    """One configuration entry per server, with scoped or admin authentication."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._configure("user", user_input)

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._configure("reauth_confirm", user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._configure("reconfigure", user_input)

    async def _configure(self, step: str, user_input: dict[str, Any] | None) -> ConfigFlowResult:
        entry = None
        if step == "reauth_confirm":
            entry = self._get_reauth_entry()
        elif step == "reconfigure":
            entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        defaults = dict(entry.data) if entry is not None else {}
        if user_input is not None:
            defaults.update(user_input)
            try:
                devices = parse_devices(user_input.get(CONF_DEVICES, ""))
                client = OttplayClient(
                    async_get_clientsession(self.hass), user_input[CONF_URL], user_input[CONF_TOKEN]
                )
                # An offline player may still be configured: the successful POST
                # authenticates the scope before the response wait times out.
                if devices:
                    try:
                        await client.async_call(devices[0], "status", {})
                    except PlayerUnavailable:
                        pass
                else:
                    await client.async_devices()
                await self.async_set_unique_id(client.url)
                if entry is None:
                    self._abort_if_unique_id_configured()
                elif any(
                    other.entry_id != entry.entry_id and other.unique_id == client.url
                    for other in self._async_current_entries()
                ):
                    return self.async_abort(reason="already_configured")
                data = {
                    CONF_URL: client.url,
                    CONF_TOKEN: user_input[CONF_TOKEN],
                    CONF_DEVICES: devices,
                }
                if entry is not None:
                    return self.async_update_reload_and_abort(
                        entry, unique_id=client.url, data_updates=data
                    )
                return self.async_create_entry(title=f"OTTPlay ({client.url})", data=data)
            except ValueError:
                errors["base"] = "invalid_input"
            except AuthError:
                errors["base"] = "invalid_auth"
            except OttplayError:
                errors["base"] = "cannot_connect"
        ids = defaults.get(CONF_DEVICES, [])
        if isinstance(ids, list):
            ids = ", ".join(ids)
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_URL, default=defaults.get(CONF_URL, "http://localhost:8081")
                ): str,
                vol.Required(CONF_TOKEN): PASSWORD,
                vol.Optional(CONF_DEVICES, default=ids): str,
            }
        )
        return self.async_show_form(step_id=step, data_schema=schema, errors=errors)

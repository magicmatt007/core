import logging

import voluptuous as vol

from homeassistant import config_entries

# from homeassistant import data_entry_flow
# from . import get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DamperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    _availableAddresses = None
    _availableAddresses = [1, 2, 3, 4]

    _availableGroups = None
    _availableGroups = ["Create a new group", "Group 1", "Group 2"]

    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        errors = {}

        if user_input is not None:
            # return self.async_abort
            return await self.async_step_finish()

        data_schema = {
            vol.Required("nextAddress"): vol.In(self._availableAddresses),
            vol.Optional("name"): str,
            vol.Optional("group"): vol.In(self._availableGroups),
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

    async def async_step_finish(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        errors = {}
        data_schema = {
            vol.Required("meal"): str,
            vol.Required("unlock", default=False): bool,
        }

        data_schema["allow_groups"]: bool

        if user_input is not None:
            print(user_input)
            if user_input["unlock"]:
                return self.async_create_entry(
                    title="Title of the entry",
                    data={"something_special": user_input["meal"]},
                )

                # return self.async_show_form(
                #     step_id="finish", data_schema=data_schema, errors=errors
                # )

            return self.async_abort(
                reason="not_supported", description_placeholders="incompatible"
            )

        # if user_input is not None:
        #     return self.async_create_entry(
        #         title=user_input[CONF_NAME],
        #         data={
        #             CONF_HOST: device.host[0],
        #             CONF_MAC: device.mac.hex(),
        #             CONF_TYPE: device.devtype,
        #             CONF_TIMEOUT: device.timeout,
        #         },
        #     )

        return self.async_show_form(
            step_id="finish", data_schema=vol.Schema(data_schema), errors=errors
        )

        # if self.show_advanced_options:
        #     data_schema["allow_groups"]: bool


# class InvalidHost(exceptions.HomeAssistantError):
#     """Error to indicate there is an invalid hostname."""
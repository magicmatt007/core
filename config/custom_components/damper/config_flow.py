import logging

import voluptuous as vol

from homeassistant import config_entries

# from homeassistant import data_entry_flow
# from . import get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
#     VERSION = 1

#     async def async_step_user(self, info):
#         if info is not None:
#             pass  # TODO: process info

#         return self.async_show_form(
#             step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
#         )

# class ExampleConfigFlow(data_entry_flow.FlowHandler):


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
            return self.async_abort

        data_schema = vol.Schema(
            {
                vol.Required("nextAddress"): vol.In(self._availableAddresses),
                vol.Optional("name"): str,
                vol.Optional("group"): vol.In(self._availableGroups),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

        # data_schema = {
        #     vol.Required("username"): str,
        #     vol.Required("password"): str,
        # }

        # return self.async_show_form(
        #     step_id="user",
        #     data_schema=vol.Schema(data_schema),
        #     errors=errors,
        # )

        # if self.show_advanced_options:
        #     data_schema["allow_groups"]: bool

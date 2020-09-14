import logging

import voluptuous as vol

from homeassistant import config_entries

# from . import get_coordinator
from .const import DOMAIN

# from homeassistant import data_entry_flow
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


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    _options = None

    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI:mm
        errors = {}

        # data_schema = {
        #     vol.Required("username"): str,
        #     vol.Required("password"): str,
        # }

        data_schema = {vol.Required("username"): str}

        # if self.show_advanced_options:
        #     data_schema["allow_groups"]: bool

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

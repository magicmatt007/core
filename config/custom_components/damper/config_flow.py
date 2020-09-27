import logging

import voluptuous as vol

from homeassistant import config_entries

# from homeassistant import data_entry_flow
# from . import get_coordinator
from .const import DOMAIN
from .hub import Hub

_LOGGER = logging.getLogger(__name__)


class DamperConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    # CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    _availableAddresses = None
    _availableAddresses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    _availableGroups = None
    _availableGroups = ["Create a new group", "Group 1", "Group 2"]

    hub = None
    FILE = None

    async def async_step_user(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        errors = {}
        print(user_input)

        FILE = self.hass.config.path("{}.pickle".format(DOMAIN))
        print(f"File in config_flow.py: {FILE}")

        if user_input is not None:
            # hub = Hub("My Hub", "/serialbyid/bla")
            self.hub = Hub(FILE, user_input["name"], user_input["com"])
            return await self.async_step_devices()

        data_schema = {
            vol.Required("name", default="Hub 1"): str,
            vol.Required("com", default="/serialbyid/blabla"): str,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

    #### From ZHA component config_flow: How to access available USB by serial on HASS:
    # TO DO: Resuse for own component

    # async def async_step_user(self, user_input=None):
    # """Handle a zha config flow start."""
    # if self._async_current_entries():
    #     return self.async_abort(reason="single_instance_allowed")

    # ports = await self.hass.async_add_executor_job(serial.tools.list_ports.comports)
    # list_of_ports = [
    #     f"{p}, s/n: {p.serial_number or 'n/a'}"
    #     + (f" - {p.manufacturer}" if p.manufacturer else "")
    #     for p in ports
    # ]
    # list_of_ports.append(CONF_MANUAL_PATH)

    # if user_input is not None:
    #     user_selection = user_input[CONF_DEVICE_PATH]
    #     if user_selection == CONF_MANUAL_PATH:
    #         return await self.async_step_pick_radio()

    #     port = ports[list_of_ports.index(user_selection)]
    #     dev_path = await self.hass.async_add_executor_job(
    #         get_serial_by_id, port.device
    #     )
    #     auto_detected_data = await detect_radios(dev_path)
    #     if auto_detected_data is not None:
    #         title = f"{port.description}, s/n: {port.serial_number or 'n/a'}"
    #         title += f" - {port.manufacturer}" if port.manufacturer else ""
    #         return self.async_create_entry(
    #             title=title,
    #             data=auto_detected_data,
    #         )

    #     # did not detect anything
    #     self._device_path = dev_path
    #     return await self.async_step_pick_radio()

    # schema = vol.Schema({vol.Required(CONF_DEVICE_PATH): vol.In(list_of_ports)})
    # return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_devices(self, user_input=None):
        # Specify items in the order they are to be displayed in the UI
        errors = {}
        print(user_input)

        if user_input is not None:
            # return self.async_abort

            if user_input["finish"]:
                # Create hass entry for the hub (this also triggers __init__.py)
                return self.async_create_entry(
                    title=self.hub.name,
                    data={"com": self.hub.com, "Comment": "Test integration"},
                )

            # Otherwise, add damper:
            self.hub.modbusAssignAddress(user_input["nextAddress"], user_input["name"])
            self.hub.print_hub()
            self._availableAddresses.remove(user_input["nextAddress"])

        data_schema = {
            vol.Required(
                "nextAddress", default=str(self._availableAddresses[0])
            ): vol.In(self._availableAddresses),
            vol.Optional(
                "name", default="Modbus " + str(self._availableAddresses[0])
            ): str,
            vol.Optional("group"): vol.In(self._availableGroups),
            vol.Optional("finish", default=False): bool,
        }

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

        # async def async_step_finish(self, user_input=None):
        #     # Specify items in the order they are to be displayed in the UI
        #     errors = {}
        #     data_schema = {
        #         vol.Required("meal"): str,
        #         vol.Required("unlock", default=False): bool,
        #     }

        #     data_schema["allow_groups"]: bool

        #     if user_input is not None:
        #         print(user_input)
        #         if user_input["unlock"]:
        #             return self.async_create_entry(
        #                 title="Title of the entry",
        #                 data={"something_special": user_input["meal"]},
        #             )

        #             # return self.async_show_form(
        #             #     step_id="finish", data_schema=data_schema, errors=errors
        #             # )

        #         return self.async_abort(
        #             reason="not_supported", description_placeholders="incompatible"
        #         )

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
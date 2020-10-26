"""The Detailed Hello World Push integration."""
import logging

_LOGGER = logging.getLogger(__name__)

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# from homeassistant.helpers import config_validation as cv, entity_platform, service

from . import hub
from .const import DOMAIN, UNDO_UPDATE_LISTENER, HUB
from datetime import timedelta

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS = ["cover", "sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Hello World component."""
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    _LOGGER.info("My first logging info message from async_setup")
    _LOGGER.warning("My first logging warning message from async_setup")
    print(f"Hello from init, async_setup. Domain: {DOMAIN}")
    print(f"Config: {config}")
    print("-----------------")

    hass.data.setdefault(DOMAIN, {})

    # Return boolean to indicate that initialization was successfully.
    return True

async def update_listener(hass, config_entry):
    """Handle options update."""
    print(f"Hello from update_listener. config_entry: {config_entry}")

    # TODO: To make this work,
    # it probalby needs to be somehow called in Cover.py and Sensor.py like in the async_setup_entry function
    # This actually calls the async_unload_entry() first, which actually deletes the pickle file that stores the hub with all dampers.
    # ... before calling the async_setup_entry(), which actaully NEEDS the pickle filre.... arghhhhh
    # See also OneNote dumps
    # -> Need to think about a different way
    await hass.config_entries.async_reload(config_entry.entry_id)


    # # TODO: Check, if this quick & dirty way of adding additional dampers via options flow creates any side effects:
    # # This creates each HA object for each platform your device requires.
    # # It's done by calling the `async_setup_entry` function in each platform module.
    # for component in PLATFORMS:
    #     hass.async_create_task(
    #         hass.config_entries.async_forward_entry_setup(config_entry, component)
    #     )

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.


    print(f"Hello from init, async_setup_entry.Domain: {DOMAIN}")
    print(f"Config Entry is: {config_entry}")

    # ## Load stored data:
    FILE = hass.config.path(f"{DOMAIN}.pickle")
    hub_obj = hub.Hub(FILE, "My Hub", "/serialbyid/bla")  # TO DO: get NAME and COM from config entry . Note: Name and Com are anyway loaded from FILE....
    hub_obj = hub_obj.get_stored_data()

    # unsub = entry.add_update_listener(update_listener)  # Required to manage updates via options flow
    undo_listener = config_entry.add_update_listener(update_listener)  # Required to manage updates via options flow
    print("Created update listener")

   # Stores a reference to the Hub instance in hass. -> Cover.py and Sensor.py can refer to it
    hass.data[DOMAIN][config_entry.entry_id] = {
        HUB: hub_obj,
        UNDO_UPDATE_LISTENER: undo_listener,
    }
    # hass.data[DOMAIN][config_entry.entry_id] = hub_obj  # Stores a reference to the Hub instance in hass. -> Cover can refer to it


    # hass.data[DOMAIN][config_entry.entry_id] = hub.Hub(hass, entry.data["com"])

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    # platform = entity_platform.current_platform.get()

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    print(f"Hello from init, async_unload_entry. Domain: {DOMAIN}")
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()
    print(f"Deleted update listener. Unload ok? {unload_ok}")

    if unload_ok:
        FILE = hass.config.path("{}.pickle".format(DOMAIN))
        print(f"File in __init__.py, unload entry: {FILE}")
        hub_obj = hub.Hub(
            FILE, "My Hub", "/serialbyid/bla"
        )  # TO DO: get NAME and COM from config entry
        hub_obj = hub_obj.delete_stored_data()

        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok

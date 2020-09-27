"""The Detailed Hello World Push integration."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import hub
from .const import DOMAIN
from datetime import timedelta

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS = ["cover", "sensor"]

# SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Hello World component."""
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    print(f"Hello from init, async_setup. Domain: {DOMAIN}")
    print(f"Config: {config}")
    hass.data.setdefault(DOMAIN, {})

    # TEMP testing:
    baloop = hass.config.path("{}.pickle".format(DOMAIN))
    print(f"Baloop: {baloop}")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
    print(f"Hello from init, async_setup_entry.Domain: {DOMAIN}")
    # print(f"Config: {entry}")
    # print(f"Config dict: {entry.__dict__}")

    # ## Load stored data:

    FILE = hass.config.path("{}.pickle".format(DOMAIN))
    print(f"File in __init__.py: {FILE}")
    hub1 = hub.Hub(
        FILE, "My Hub", "/serialbyid/bla"
    )  # TO DO: get NAME and COM from config entry
    hub1 = hub1.get_stored_data()
    hub1.print_dampers()

    hass.data[DOMAIN][entry.entry_id] = hub1
    # hass.data[DOMAIN][entry.entry_id] = hub.Hub(hass, entry.data["com"])

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    print(f"Hello from init, async_unload_entry. Domain: {DOMAIN}")
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

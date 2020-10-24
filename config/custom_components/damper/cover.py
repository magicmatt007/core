"""Platform for sensor integration."""
import logging

_LOGGER = logging.getLogger(__name__)

import asyncio
import time
import voluptuous as vol

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    DEVICE_CLASS_DAMPER,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    SUPPORT_SET_TILT_POSITION,
    SUPPORT_OPEN_TILT,
    SUPPORT_CLOSE_TILT,
    SUPPORT_STOP_TILT,
    SUPPORT_STOP,
    CoverEntity,
)
from homeassistant.const import (
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
    TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv, entity_platform, service

from .const import DOMAIN
from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=1)
SERVICE_TEST_DAMPER = "test_damper"

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add cover for passed config_entry in HA."""
    print("hello from cover, async_setup_entry")

    # The reference to the Hub instance is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function:
    hub_obj = hass.data[DOMAIN][config_entry.entry_id]

    # The next few lines find all of the entities that will need to be added to HA.
    # Note these are all added to a list, so async_add_devices needs to be called just once.
    new_devices = []
    for damper in hub_obj.dampers:
        cover_obj = Cover(damper) # Creates a (Damper)Cover instance for each Damper instance in Hub
        new_devices.append(cover_obj)
    if new_devices: # If we have any new devices, add them
        async_add_devices(new_devices)

    # TO DO: Open Damper when started:
    # for cover_obj in new_devices:
    #     await cover_obj.async_open_cover()


    # Register Services:
    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(SERVICE_TEST_DAMPER,{},"test_damper",)  # This service will call test_damper() on the instance


class Cover(CoverEntity):
    """Representation of a Cover."""

    should_poll = True

    def __init__(self, damper): # Create a Cover instance, which stores a reference to the Damper instance
        """Initialize the damper."""
        self._damper = damper  # instance of class damper, stored in hub.py
        self._state = None  # state must be initialized here already.  STATE_CLOSED
        # # Removed this init values, as the update()) function takes care of it:
        # self._current_position = 0
        # self._is_closed = True
        # self._is_open = False
        # self._is_opening = False
        # self._is_closing = False

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self._damper._modbus_address}_cover"  # TO DO: Make it a real UID. Current implementation could lead to duplicates, if config flow doesn't ensure uniqure modbus addresses (which is currently does)

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._damper._modbus_address)},
            "name": self._damper.name,
            "sw_version": self._damper._factory_index,
            "model": self._damper._type_asn,
            "manufacturer": self._damper.manufacturer,
        }

    @property
    def name(self):
        """Return the name of the damper."""
        return self._damper.name

    @property
    def state(self):
        """Return the state of the damper."""
        return self._state

    @property
    def is_open(self):
        """Return the open state of the damper."""
        return self._is_open

    @property
    def is_closed(self):
        """Return the closed state of the damper."""
        return self._is_closed

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return self._is_opening

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return self._is_closing

    @property
    def current_cover_position(self):
        """Return the closed state of the damper."""
        return self._damper.position

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_DAMPER

    @property
    def supported_features(self):
        """Return the supported features."""

        return (
            SUPPORT_CLOSE
            | SUPPORT_OPEN
            | SUPPORT_SET_POSITION
            | SUPPORT_STOP
            | SUPPORT_OPEN_TILT
        )  # TO DO: SUPPORT_STOP is misused to start testing...

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        self._damper._attributes = {
            "Modbus Address": self._damper._modbus_address,
            "Type ASN": self._damper._type_asn,
            "Manufacturing Date": self._damper._manufacturing_date,
            "Factory Index": self._damper._factory_index,
            "Factory Seq Num": self._damper._factory_seq_num,
            "Last runtime close": self._damper._runtime_close,
            "Last runtime open": self._damper._runtime_open,
            "Last power": self._damper._power,
            "Last overall indicator": self._damper._overall_indicator,
            "Last runtime close indicator": self._damper._runtime_close_indicator,
            "Last runtime open indicator": self._damper._runtime_open_indicator,
            "Last power indicator": self._damper._power_indicator,
            "Last tested at": self._damper._tested_at,
        }
        return self._damper._attributes

        # TIP: https://developers.home-assistant.io/docs/dev_101_states
        # Entities also have a similar property state_attributes, which normally doesn't need to be defined by new platforms.
        # This property is used by base components to add standard sets of attributes to a state.
        # Example: The light component uses state_attributes to add brightness to the state dictionary. If you are designing a new component, you should define state_attributes instead.

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self._damper.set_position(100)

    async def async_open_cover_tilt(self, **kwargs):  # ADDED for testing UI only. No implementation!
        """Open the cover tilt."""
        return

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        await self._damper.set_position(kwargs[ATTR_POSITION])

    async def async_close_cover(self, **kwargs):
        """Close the cover."""

        ########################
        # Accomdate for the dodgy spring return set-point implementation in Sep 2020.
        # Setpoint:
        # 0 - 1000 = Spring return close
        # 2000 - 10000 = 0 - 100%
        # NOTE: target_positon is in [0,100]. The conversion to [0, 10000] happens in the hub.py
        if (self._damper._type_asn[0:6] == "GMA151") or (
            self._damper._type_asn[0:6] == ""
        ):
            await self._damper.spring_close()
        else:
            await self._damper.set_position(0)

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        ### TO DO: Missused for triggering testing.....

        await self._damper.modbus_test()

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # print("Hello from async_update")

        await self._damper.update()

        self._current_position = self._damper.position
        self._is_closed = self._damper._is_closed
        self._is_open = self._damper._is_open
        self._is_closing = self._damper._is_closing
        self._is_opening = self._damper._is_opening

        if self._is_closed:
            self._state = STATE_CLOSED
        elif self.is_open:
            self._state = STATE_OPEN
        elif self.is_closing:
            self._state = STATE_CLOSING
        elif self.is_opening:
            self._state = STATE_OPENING
        else:
            self._state = (
                "UNKNOWN!"  # TODO: Is there an official Hassio state for this case??
            )

    async def test_damper(self):
        print("Hello from test_damper service")
        _LOGGER.debug("Hello from test_damper service")
        await self._damper.modbus_test()
        return
"""Platform for sensor integration."""
import asyncio
import time

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

from .const import DOMAIN

from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=1)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add cover for passed config_entry in HA."""
    print("hello from cover, async_setup_entry")

    # The hub is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    hub = hass.data[DOMAIN][config_entry.entry_id]

    # The next few lines find all of the entities that will need to be added
    # to HA. Note these are all added to a list, so async_add_devices can be
    # called just once.
    new_devices = []
    for damper in hub.dampers:
        print(f"Damper DICT: {damper.__dict__}")
        damper_entity = DamperCover(damper)
        new_devices.append(damper_entity)
    # If we have any new devices, add them
    if new_devices:
        async_add_devices(new_devices)


class DamperCover(CoverEntity):
    """Representation of a Cover."""

    should_poll = True

    def __init__(self, damper):
        """Initialize the damper."""
        self._damper = damper  # instance of class damper, stored in hub.py

        # These attributes are currently not in the damper class. Should these be added??????
        self._state = STATE_CLOSED
        self._is_closed = True
        self._is_opening = False
        self._is_closing = False
        self._is_open = False
        self._is_closed = False

        # Additional custom attributes for the Damper implementation of Cover:
        # Note: The value of these attributes are loaded from the damper object
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
        }

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self._damper._modbus_address}_cover"  # TO DO: Make it a real UID. Current implementation could lead to duplicates, if config flow doesn't ensure uniqure modbus addresses (which is currently does)

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._damper._modbus_address)},
            # If desired, the name for the device could be different to the entity
            "name": self._damper.name,
            "sw_version": self._damper._factory_index,
            "model": self._damper._type_asn,
            "manufacturer": self._damper.manufacturer,
        }

    @property
    def name(self):
        """Return the name of the damper."""
        # return 'Example Damper'
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
        # print(f"Hello from damper.current_cover_position {time.time()}")
        return self._damper.position

    # @property
    # def unit_of_measurement(self):
    #     """Return the unit of measurement."""
    #     return TEMP_CELSIUS

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
            "Last runtime open indiator": self._damper._runtime_open_indicator,
            "Last power indicator": self._damper._power_indicator,
        }
        return self._damper._attributes

        # TIP: https://developers.home-assistant.io/docs/dev_101_states
        # Entities also have a similar property state_attributes, which normally doesn't need to be defined by new platforms.
        # This property is used by base components to add standard sets of attributes to a state.
        # Example: The light component uses state_attributes to add brightness to the state dictionary. If you are designing a new component, you should define state_attributes instead.

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        self._state = STATE_OPENING
        self._is_opening = True
        self._is_closing = False
        await self._damper.set_position(100)

    async def async_open_cover_tilt(
        self, **kwargs
    ):  # ADDED for testing UI only. No implementation!
        """Open the cover tilt."""
        print("Hello from async_open_cover_tilt")
        return

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        target_position = kwargs[ATTR_POSITION]
        if target_position > self._damper.position:
            self._state = STATE_OPENING
            self._is_opening = True
            self._is_closing = False
        elif target_position < self._damper.position:
            self._state = STATE_CLOSING
            self._is_closing = True
            self._is_opening = False

        await self._damper.set_position(kwargs[ATTR_POSITION])

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        self._state = STATE_CLOSING
        self._is_closing = True
        self._is_opening = False

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

        self._state = STATE_CLOSING
        self._is_closing = True
        self._is_opening = False

        await self._damper.modbus_test()

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # print("Hello from async_update")

        await self._damper.update()

        _current_position = self._damper.position

        if _current_position > 95:
            self._state = STATE_OPEN
            self._is_open = True
            self._is_closed = False
        elif _current_position < 5:
            self._state = STATE_CLOSED
            self._is_closed = True
            self._is_open = False
        else:
            self._is_closed = False
            self._is_open = False

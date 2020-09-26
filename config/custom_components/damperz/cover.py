"""Platform for sensor integration."""
import asyncio

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    DEVICE_CLASS_DAMPER,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    SUPPORT_SET_TILT_POSITION,
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

from . import modbusAutoAddress
from .modbusInstrument import ModbusInstrument

# # Imports for Modbus:
# import minimalmodbus # as mmRtu
# import serial
# import time
# from datetime import date

############################################


override_off = 0
override_open = 1
override_close = 2
override_stop = 3
override_GoToMin = 4
override_GoToMax = 5


####################################


# async def async_setup(hass: HomeAssistant, config: dict):
#     """Set up the Hello World component."""
#     # Ensure our name space for storing objects is a known type. A dict is
#     # common/preferred as it allows a separate instance of your class for each
#     # instance that has been created in the UI.
#     hass.data.setdefault(DOMAIN, {})

#     return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add cover for passed config_entry in HA."""
    print("hello world")
    async_add_devices([ExampleDamper("Damper 1", 1)])


# async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#     """Set up the sensor platform."""
#     async_add_entities([ExampleDamper("Damper 1", 1)])
#     # add_entities([ExampleDamper("Damper 2",2)])
#     async_add_entities([ExampleDamper("Damper 3", 103)])


## TO DO: Implement routine to add dampers, which were added via config_flow and are persistantly stored in a pickle file:
# import hub
# for damper in DAMPERS:
#    add_entities(FireDamper(damper.name, damper.modbus_address))


# class ExampleDamper(Entity):
class ExampleDamper(CoverEntity):
    """Representation of a Cover."""

    def __init__(self, name, modbus_address):
        """Initialize the sensor."""
        self._name = name
        self._modbus_address = modbus_address
        self._state = STATE_CLOSED
        self._current_cover_position = 0
        self._is_closed = True
        self._is_opening = False
        self._is_closing = True
        # Additional custom attributes for the Damper implementation of Cover:
        self._attributes = {"Custom 1": 1, "Custom 2": "Hello World"}

    @property
    def name(self):
        """Return the name of the sensor."""
        # return 'Example Damper'
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

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
        return self._current_cover_position

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
        """Return the device class."""

        return SUPPORT_CLOSE | SUPPORT_OPEN | SUPPORT_SET_POSITION

    @property
    def position_ms(self):
        """Return the device class."""
        return self._current_cover_position

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return self._attributes

        # TIP: https://developers.home-assistant.io/docs/dev_101_states
        # Entities also have a similar property state_attributes, which normally doesn't need to be defined by new platforms.
        # This property is used by base components to add standard sets of attributes to a state.
        # Example: The light component uses state_attributes to add brightness to the state dictionary. If you are designing a new component, you should define state_attributes instead.

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        self._state = STATE_OPENING
        self._is_opening = True

        # while(self._current_cover_position < 100):
        #     self._current_cover_position += 1
        #     await asyncio.sleep(0.1)
        # self._state = STATE_OPEN

        # self._current_cover_position = 100

        instruments = []
        instruments.append(
            ModbusInstrument(self._modbus_address)
        )  # Create new instrument with address 5 and append it to the instruments array, that keeps all connected devices
        i = instruments[0]
        i.setpoint(10000)

    async def async_close_cover(self, **kwargs):
        """Open the cover."""
        self._state = STATE_CLOSING
        self._is_closing = True

        # while(self._current_cover_position > 0):
        #     self._current_cover_position += -1
        #     await asyncio.sleep(0.1)

        # self._state = STATE_CLOSED
        # self._current_cover_position = 0

        instruments = []
        instruments.append(
            ModbusInstrument(self._modbus_address)
        )  # Create new instrument with address 5 and append it to the instruments array, that keeps all connected devices
        i = instruments[0]
        i.setpoint(0)

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""

        self._current_cover_position = kwargs[ATTR_POSITION]
        if self._current_cover_position == 0:
            self._state = STATE_CLOSED
        else:
            self._state = STATE_OPEN

        # # Modbus RTU tests: ###########################################

        instruments = []
        instruments.append(
            ModbusInstrument(self._modbus_address)
        )  # Create new instrument with address 5 and append it to the instruments array, that keeps all connected devices
        # print(f"Total instruments: {instruments[0].instrumentCount}")

        i = instruments[0]
        # print(f"Instrument Model: {i.typeASN()}")
        # print(f"Manufacturing date: {i.factoryDate()}")
        # print(f"Factory Index: {i.factoryIndex()}")
        # print(f"Factory Sequence Number: {i.factorySeqNum()}")
        # # print(f"Factory Index: {i.factoryIndex():X}")

        # i.overrideControl(override_off)
        # i.setpoint(6000)
        i.setpoint(self._current_cover_position * 100)

        # # i.monitorPositionChange()
        # print(f"Current Position: {(i.actualPosition()/10000*90):1f}°")

        # # Modbus RTU tests: ###########################################

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """

        instruments = []
        instruments.append(
            ModbusInstrument(self._modbus_address)
        )  # Create new instrument with address 5 and append it to the instruments array, that keeps all connected devices
        i = instruments[0]
        self._current_cover_position = i.actualPosition() / 100

        # self._state = 23
        await asyncio.sleep(0.1)

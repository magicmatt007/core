"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import random

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    # UNIT_PERCENTAGE,
    DEVICE_CLASS_ILLUMINANCE,
)
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, HUB

from homeassistant.const import ATTR_VOLTAGE

from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=1)

UNIT_PERCENTAGE = "%"

# See cover.py for more details.
# Note how both entities for each damper sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.
async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    # hub = hass.data[DOMAIN][config_entry.entry_id]
    hub_obj = hass.data[DOMAIN][config_entry.entry_id][HUB]


    new_devices = []
    for damper in hub_obj.dampers:
        new_devices.append(PositionSensor(damper))
        # new_devices.append(BatterySensor(damper))
        # new_devices.append(IlluminanceSensor(damper))
    if new_devices:
        async_add_devices(new_devices)


# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.
class SensorBase(Entity):
    """Base representation of a Hello World Sensor."""

    should_poll = True

    def __init__(self, damper):
        """Initialize the sensor."""
        self._damper = damper

    # To link this entity to the cover device, this property must return an
    # identifiers value matching that used in the cover, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._damper._modbus_address)}}
        # return {"identifiers": {(DOMAIN, self._damper.damper_id)}}

    # # This property is important to let HA know if this entity is online or not.
    # # If an entity is offline (return False), the UI will refelect this.
    # @property
    # def available(self) -> bool:
    #     """Return True if damper and hub is available."""
    #     return self._damper.online and self._damper.hub_obj.online

    # async def async_added_to_hass(self):
    #     """Run when this Entity has been added to HA."""
    #     # Sensors should also register callbacks to HA when their state changes
    #     self._damper.register_callback(self.async_write_ha_state)

    # async def async_will_remove_from_hass(self):
    #     """Entity being removed from hass."""
    #     # The opposite of async_added_to_hass. Remove any registered call backs here.
    #     self._damper.remove_callback(self.async_write_ha_state)


class PositionSensor(SensorBase):
    """Representation of a Sensor."""

    # The class of this device. Note the value should come from the homeassistant.const
    # module. More information on the available devices classes can be seen here:
    # https://developers.home-assistant.io/docs/core/entity/sensor

    # device_class = DEVICE_CLASS_BATTERY    # No suitable device class available for position

    def __init__(self, damper):
        """Initialize the sensor."""
        super().__init__(damper)
        self._state = random.randint(
            0, 100
        )  # TO DO: Replace with position from hub_obj.damper

    # As per the sensor, this must be a unique value within this domain. This is done
    # by using the device ID, and appending "_battery"
    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self._damper._modbus_address}_position"  # TO DO: Make it a real UID. Current implementation could lead to duplicates, if config flow doesn't ensure uniqure modbus addresses (which is currently does)

    # @property
    # def unique_id(self):
    #     """Return Unique ID string."""
    #     return f"{self._damper.damper_id}_battery"

    # This property can return additional metadata about this device. Here it's
    # returning the voltage of the battery. The actual percentage is returned in
    # the state property below. These values are displayed in the entity details
    # screen at the bottom below the history graph.
    # A number of defined attributes are available, see the homeassistant.const module
    # for constants starting with ATTR_*.
    # Again, if these values change, the async_write_ha_state method should be called.
    # in this implementation, these values are assumed to be static.
    # Note this functionality to display addition data on an entity appears to be
    # exclusive to sensors. This information is not shown in the UI for a cover.
    # @property
    # def device_state_attributes(self):
    #     """Return the state attributes of the device."""
    #     attr = {}
    #     attr[ATTR_VOLTAGE] = self._damper.battery_voltage
    #     return attr

    # The value of this sensor. As this is a DEVICE_CLASS_BATTERY, this value must be
    # the battery level as a percentage (between 0 and 100)
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._damper.position
        # return self._damper.battery_level

    # The unit of measurement for this entity. As it's a DEVICE_CLASS_BATTERY, this
    # should be UNIT_PERCENTAGE. A number of units are supported by HA, for some
    # examples, see:
    # https://developers.home-assistant.io/docs/core/entity/sensor#available-device-classes
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UNIT_PERCENTAGE

    # The same of this entity, as displayed in the entity UI.
    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._damper.name} Position"
        # return f"{self._damper.name} Battery"

    # # Might not need this, as the cover.py already calls the update method of damper....
    # async def async_update(self):
    #     """Fetch new state data for the sensor.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     print("Hello from async_update sensor")

    #     await self._damper.update()


# class BatterySensor(SensorBase):
#     """Representation of a Sensor."""

#     # The class of this device. Note the value should come from the homeassistant.const
#     # module. More information on the available devices classes can be seen here:
#     # https://developers.home-assistant.io/docs/core/entity/sensor
#     device_class = DEVICE_CLASS_BATTERY

#     def __init__(self, damper):
#         """Initialize the sensor."""
#         super().__init__(damper)
#         self._state = random.randint(0, 100)

#     # As per the sensor, this must be a unique value within this domain. This is done
#     # by using the device ID, and appending "_battery"
#     @property
#     def unique_id(self):
#         """Return Unique ID string."""
#         return f"{self._damper.damper_id}_battery"

#     # This property can return additional metadata about this device. Here it's
#     # returning the voltage of the battery. The actual percentage is returned in
#     # the state property below. These values are displayed in the entity details
#     # screen at the bottom below the history graph.
#     # A number of defined attributes are available, see the homeassistant.const module
#     # for constants starting with ATTR_*.
#     # Again, if these values change, the async_write_ha_state method should be called.
#     # in this implementation, these values are assumed to be static.
#     # Note this functionality to display addition data on an entity appears to be
#     # exclusive to sensors. This information is not shown in the UI for a cover.
#     @property
#     def device_state_attributes(self):
#         """Return the state attributes of the device."""
#         attr = {}
#         attr[ATTR_VOLTAGE] = self._damper.battery_voltage
#         return attr

#     # The value of this sensor. As this is a DEVICE_CLASS_BATTERY, this value must be
#     # the battery level as a percentage (between 0 and 100)
#     @property
#     def state(self):
#         """Return the state of the sensor."""
#         return self._damper.battery_level

#     # The unit of measurement for this entity. As it's a DEVICE_CLASS_BATTERY, this
#     # should be UNIT_PERCENTAGE. A number of units are supported by HA, for some
#     # examples, see:
#     # https://developers.home-assistant.io/docs/core/entity/sensor#available-device-classes
#     @property
#     def unit_of_measurement(self):
#         """Return the unit of measurement."""
#         return UNIT_PERCENTAGE

#     # The same of this entity, as displayed in the entity UI.
#     @property
#     def name(self):
#         """Return the name of the sensor."""
#         return f"{self._damper.name} Battery"


# # This is another sensor, but more simple compared to the battery above. See the
# # comments above for how each field works.
# class IlluminanceSensor(SensorBase):
#     """Representation of a Sensor."""

#     device_class = DEVICE_CLASS_ILLUMINANCE

#     @property
#     def unique_id(self):
#         """Return Unique ID string."""
#         return f"{self._damper.damper_id}_illuminance"

#     @property
#     def name(self):
#         """Return the name of the sensor."""
#         return f"{self._damper.name} Illuminance"

#     @property
#     def state(self):
#         """Return the state of the sensor."""
#         return self._damper.illuminance

#     @property
#     def unit_of_measurement(self):
#         """Return the unit of measurement."""
#         return "lx"

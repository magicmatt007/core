"""A demonstration 'hub' that connects several devices."""
# In a real implementation, this would be in an external library that's on PyPI.
# The PyPI package needs to be included in the `requirements` section of manifest.json
# See https://developers.home-assistant.io/docs/creating_integration_manifest
# for more information.
# This dummy hub always returns 3 rollers.
import asyncio
import random


class Hub:
    """Dummy hub for Hello World example."""

    manufacturer = "Demonstration Corp"

    def __init__(self, hass, host):
        """Init dummy hub."""
        self._host = host
        self._hass = hass
        self._name = host
        self._id = host.lower()
        self.rollers = [
            Roller(f"{self._id}_1", f"{self._name} 1", self),
            Roller(f"{self._id}_2", f"{self._name} 2", self),
            Roller(f"{self._id}_3", f"{self._name} 3", self),
        ]
        self.online = True

    @property
    def hub_id(self):
        """ID for dummy hub."""
        return self._id

    async def test_connection(self):
        """Test connectivity to the Dummy hub is OK."""
        await asyncio.sleep(1)
        return True


class Roller:
    """Dummy roller (device for HA) for Hello World example."""

    def __init__(self, rollerid, name, hub):
        """Init dummy roller."""
        self._id = rollerid
        self.hub = hub
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        self._target_position = 100
        self._current_position = 100
        # Reports if the roller is moving up or down.
        # >0 is up, <0 is down. This very much just for demonstration.
        self.moving = 0

        # Some static information about this device
        self.firmware_version = "0.0.{}".format(random.randint(1, 9))
        self.model = "Test Device"

    @property
    def roller_id(self):
        """Return ID for roller."""
        return self._id

    @property
    def position(self):
        """Return position for roller."""
        return self._current_position

    async def set_position(self, position):
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        self._target_position = position

        # Update the moving status, and broadcast the update
        self.moving = position - 50
        await self.publish_updates()

        self._loop.create_task(self.delayed_update())

    async def delayed_update(self):
        """Publish updates, with a random delay to emulate interaction with device."""
        print(f"{self._id}: Start Sleeping....")
        await asyncio.sleep(random.randint(1, 10))
        print(f"{self._id}: End Sleeping....")
        self.moving = 0
        await self.publish_updates()

    def register_callback(self, callback):
        """Register callback, called when Roller changes state."""
        print(f"{self._id}: Register callback....")
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self):
        """Schedule call all registered callbacks."""
        print(f"{self._id}: Publish updates....")
        self._current_position = self._target_position
        for callback in self._callbacks:
            print(f"{self._id}: Publish updates CALLBACK()....")
            callback()

    # BACnet stuff:
    @property
    def present_value(self):
        """Return BACnet property present value"""
        return random.randint(0, 500)

    @property
    def description(self):
        """Return BACnet property description"""
        return f"Description {self._id}"

    @property
    def object_name(self):
        """Return BACnet property object name"""
        return f"Object name {self._id}"

    @property
    def object_identifier(self):
        """Return BACnet object identifier"""
        return f"Object identifier {self._id}"

    # Template stuff. TODO: Remove

    @property
    def online(self):
        """Roller is online."""
        # The dummy roller is offline about 10% of the time. Returns True if online,
        # False if offline.
        return random.random() > 0.1

    @property
    def battery_level(self):
        """Battery level as a percentage."""
        return random.randint(0, 100)

    @property
    def battery_voltage(self):
        """Return a random voltage roughly that of a 12v battery."""
        return round(random.random() * 3 + 10, 2)

    @property
    def illuminance(self):
        """Return a sample illuminance in lux."""
        return random.randint(0, 500)

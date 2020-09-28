import asyncio
import time
import pickle
from logging import getLogger
from os.path import exists, join
import os
from homeassistant.core import HomeAssistant

from homeassistant.config import get_default_config_dir
from .const import (
    DOMAIN,
    VIRTUAL_MODBUS_DEBUG,
)  # might need to remove the . from .const, when running in homeassistant instead of command line

import json

### Imports from within this project:
from .modbusAutoAddress import *

from .modbusInstrument import ModbusInstrument

# DEBUGGING: python -m config.custom_components.damper.hub

# https://pythonexamples.org/python-pickle-class-object/
# https://stackoverflow.com/questions/44166092/why-is-pickle-not-serializing-my-array-of-classes
# https://github.com/shaftoe/home-assistant-custom-components/blob/4fc91d69cd9a99dc2d1facbab6aefa45832d7edc/spreaker2sonos.py

config_dir = os.path.join(os.getcwd())
print(f"OS based dir: {config_dir}")


class Hub:
    manufacturer = "Demonstration Corp"

    # def __init__(self,damper):
    def __init__(self, FILE, name, com):
        # self.Main = None
        # self._hass = hass
        print(f"FILE in hub init: {FILE}")
        self.FILE = FILE
        self._name = name
        self._com = com
        self.dampers = []

    @property
    def name(self):
        """Return name string."""
        return self._name

    @property
    def com(self):
        """Return com string."""
        return self._com

    def addNewDamperToDb(
        self,
        newSlaveAddress,
        name,
        type_asn,
        manufacturing_date,
        factory_index,
        factory_seq_num,
    ):
        damper = Damper(
            name,
            newSlaveAddress,
            type_asn,
            manufacturing_date,
            factory_index,
            factory_seq_num,
        )
        self.dampers.append(damper)
        self.store()

    def modbusAssignAddress(self, nextAddress, name=None):

        # VIRTUAL_MODBUS_DEBUG = True  ## used to test without a Modbus USB stick

        #### Values for push button config:  ####
        newSlaveAddress = nextAddress
        newBaudrate = 2  # 0 = auto / 1 = 9600 / 2 = 19200 3 = 38400 / 4 = 57600 / 5 = 76800  6 = 115200
        newTransmittionMode = 2  # 2 = 1-8-N-1
        newTermination = 0  # 0 = off   1 = on
        #### end #####

        try:
            if not VIRTUAL_MODBUS_DEBUG:
                success = configureSlave(  # modbusAutoAddress.configureSlave(
                    newSlaveAddress, newBaudrate, newTransmittionMode, newTermination
                )
            else:
                success = True

            time.sleep(3)  # added temporarily for debugging GDB111.1E/MO

            if success:
                if not VIRTUAL_MODBUS_DEBUG:
                    instrument = ModbusInstrument(newSlaveAddress)
                    type_asn = instrument.typeASN()
                    manufacturing_date = str(
                        instrument.factoryDate()
                    )  # Convert to str. Date object not serializable to JSON in HASSIO
                    factory_index = instrument.factoryIndex()
                    factory_seq_num = instrument.factorySeqNum()
                else:
                    type_asn = "GRA126"
                    manufacturing_date = "31.12.2020"
                    factory_index = "A"
                    factory_seq_num = "01234567890"

                if not name:  # If no name is provided by the user, then auto assign
                    name = f"Modbus {newSlaveAddress}"  # TODO: get name from user input

                self.addNewDamperToDb(
                    newSlaveAddress,
                    name,
                    type_asn,
                    manufacturing_date,
                    factory_index,
                    factory_seq_num,
                )

            return success

        except Exception as e:
            print(
                "Error (modbusAssignAddr). Have you connected the Modbus interface?"
                + str(e)
            )

            return False

    def print_hub(self):
        # print(hub.Main.__dict__)
        print(f"Name: {self._name}")
        print(f"COM: {self._com}")
        for damper in self.dampers:
            print(damper.__dict__)

    def store(self):
        print("Saving data...")
        print(f"FILE = {self.FILE}")

        # """Store to file."""
        with open(self.FILE, "wb") as myfile:
            pickle.dump(self, myfile, pickle.HIGHEST_PROTOCOL)
        myfile.close()

    def get_stored_data(self):
        """Return stored data."""
        if not exists(self.FILE):
            print("File doesn't exist")
            return {}
        print("Loading data...")
        print(f"self.FILE = {self.FILE}")
        with open(self.FILE, "rb") as myfile:
            content = pickle.load(myfile)
        myfile.close()
        return content

    def print_dampers(self):
        for damper in self.dampers:
            print(damper.__dict__)

    def print_damper(self, damper):
        print(damper.__dict__)


class Damper:
    # _name: str
    # _id: int
    # _is_closed: bool
    # _is_open: bool
    # _modbus_address: int

    manufacturer = "Siemens"

    def __init__(
        self,
        name,
        modbus_address,
        type_asn,
        manufacturing_date,
        factory_index,
        factory_seq_num,
    ):
        self.name = name
        self._modbus_address = modbus_address
        self._type_asn = type_asn
        self._manufacturing_date = manufacturing_date
        self._factory_index = factory_index
        self._factory_seq_num = factory_seq_num

        self._id = 1  # TO DO: Remove or do a proper implementation
        self._is_closed = True
        self._is_open = False

        self._target_position = 0
        self._current_position = 0

    @property
    def position(self):
        """Return position for roller."""
        return self._current_position

    async def set_position(self, position):
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        print(f"Hello from hub.damper.set_position({position})")

        ########################
        # Accomdate for the dodgy spring return set-point implementation in Sep 2020.
        # Setpoint:
        # 0 - 1000 = Spring return close
        # 2000 - 10000 = 0 - 100%
        # NOTE: target_positon is in [0,100]. The conversion to [0, 10000] happens in the hub.py
        # TO DO: Understand, why the logic seem to be required here in hub.py/Damper and not in cover.py
        if self._type_asn[0:6] == "GMA151" or "":
            print(f"Adjusting setpoint {self._type_asn[0:6]}, {position}")
            position = int(position * 0.8 + 20)
            print(f"New setpoint {position}")
            # target_position = round((target_position * 0.8 + 2000),0)
        else:
            print(f"No setpoint adjustment {self._type_asn[0:6]}, {position}")

        self._target_position = position
        if self._target_position > self._current_position:
            print("Opening")
            virtual_direction = 1
        elif self._target_position < self._current_position:
            print("Closing")
            virtual_direction = -1

        if not VIRTUAL_MODBUS_DEBUG:
            i = ModbusInstrument(self._modbus_address)
            i.setpoint(position * 100)
        else:
            while (self._current_position - self._target_position) != 0:
                self._current_position += 1 * virtual_direction
                print(f"Current Position: {self._current_position}")
                await asyncio.sleep(0.1)

        # self._target_position = position

    async def update(self):
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        print("Hello from hub.damper.update(...)")

        if not VIRTUAL_MODBUS_DEBUG:
            i = ModbusInstrument(self._modbus_address)
            self._current_position = i.actualPosition() / 100
        else:
            await asyncio.sleep(0.1)
            self._current_position = self._current_position


if __name__ == "__main__":
    print("hello from __main__")

    # hub = Hub("My Hub", "/serialbyid/bla")
    # hub.modbusAssignAddress(1)
    # hub.print_hub()

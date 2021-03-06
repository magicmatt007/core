import asyncio
import time
import pickle
from random import randint

from logging import getLogger
from os.path import exists, join
import os
from homeassistant.core import HomeAssistant

from homeassistant.config import get_default_config_dir
from .const import (
    DOMAIN,
    VIRTUAL_MODBUS_DEBUG,
    VIRTUAL_RUNTIME_OPEN,
    VIRTUAL_RUNTIME_CLOSE,
    VIRTUAL_RUNTIME_VAR_PERCENT,
)  # might need to remove the . from .const, when running in homeassistant instead of command line

import json
import asyncio

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
        # Attributes:
        self._type_asn = type_asn
        self._manufacturing_date = manufacturing_date
        self._factory_index = factory_index
        self._factory_seq_num = factory_seq_num

        # Testing:
        self._runtime_open = None
        self._runtime_close = None
        self._power = None
        self._overall_indicator = None
        self._runtime_close_indicator = None
        self._runtime_open_indicator = None
        self._power_indicator = None
        # self._runtime_open: float
        # self._runtime_close: float
        # self._power: float
        # self._overall_indicator: str
        # self._runtime_close_indicator: str
        # self._runtime_open_indicator: str
        # self._power_indicator: str

        # States:
        self._id = 1  # TO DO: Remove or do a proper implementation
        self._is_closed = True
        self._is_open = False

        self._target_position = 0
        self._current_position = 0
        self._currently_testing = False

        print(f"Damper DICT in Damper.__init__: {self.__dict__}")

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
        if (self._type_asn[0:6] == "GMA151") or (self._type_asn[0:6] == ""):
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

    async def spring_close(self):
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        print(f"Hello from hub.damper.spring_close()")

        virtual_direction = -1

        if not VIRTUAL_MODBUS_DEBUG:
            i = ModbusInstrument(self._modbus_address)
            i.setpoint(0)
        else:
            while (self._current_position - self._target_position) != 0:
                self._current_position += 1 * virtual_direction
                print(f"Current Position: {self._current_position}")
                await asyncio.sleep(0.05)


    async def update(self):
        """
        Set dummy cover to the given position.

        State is announced a random number of seconds later.
        """
        # print("Hello from hub.damper.update(...)")

        if not VIRTUAL_MODBUS_DEBUG:
            i = ModbusInstrument(self._modbus_address)
            self._current_position = i.actualPosition() / 100
        else:
            # await asyncio.sleep(0.1)
            self._current_position = self._current_position

    async def modbus_test(self):

        print(f"Hello from hub.damper.modbus_test Modbus ({self._modbus_address})")

        if self._currently_testing:
            print(
                f"Damper is already testing. Please wait {self.name}, {self._modbus_address}"
            )
            return
        else:
            print(
                f"Damper is not yet testing. Starting now {self.name}, {self._modbus_address}"
            )

        # Close Damper:
        if VIRTUAL_MODBUS_DEBUG:
            _runtime_close = (
                VIRTUAL_RUNTIME_CLOSE
                * (
                    100
                    + randint(-VIRTUAL_RUNTIME_VAR_PERCENT, VIRTUAL_RUNTIME_VAR_PERCENT)
                )
                / 100
            )

            _, self._runtime_close = await asyncio.gather(
                self.virtual_position(0, _runtime_close), self.test_damper(90, 0)
            )
            # print(f"A: {a}")
            # print(f"b: {b}")
        else:
            self._runtime_close = await self.test_damper(90, 0)

        print("Preparing for opening...")
        await asyncio.sleep(5)

        # Open Damper:
        if VIRTUAL_MODBUS_DEBUG:
            _runtime_open = (
                VIRTUAL_RUNTIME_OPEN
                * (
                    100
                    + randint(-VIRTUAL_RUNTIME_VAR_PERCENT, VIRTUAL_RUNTIME_VAR_PERCENT)
                )
                / 100
            )

            _, self._runtime_open = await asyncio.gather(
                self.virtual_position(100, _runtime_open), self.test_damper(90, 100)
            )
        else:
            self._runtime_open = await self.test_damper(90, 100)

    async def virtual_position(self, position, runtime):
        if self._current_position < position:
            while self._current_position < position:
                self._current_position += 1
                await asyncio.sleep(runtime / 100)
        else:
            while self._current_position > position:
                self._current_position += -1
                await asyncio.sleep(runtime / 100)

    async def test_damper(self, runtime_max, target_position):
        RUNTIME_MAX = runtime_max
        INTERVAL = 1
        global error_count
        error_count = 0
        # global dampers_currently_testing
        error = ""

        #### Close or Open Damper:
        try:
            startTime = time.time()

            if not VIRTUAL_MODBUS_DEBUG:
                await self.set_position(target_position)
                if target_position == 0:
                    await self.spring_close()  # TO DO: Consider better coding....
                    if self._type_asn[0:6] == "GDB111":
                        print("Hello from GDB111 sleeping....")
                        await asyncio.sleep(10)
                        print("Woke up...")
                else:
                    await self.set_position(target_position)

            # data["state"] = "Closing"
            # TO DO: How to handle update of cover attributes like state, is_closing, ...?
            #        Should these be replicated in hub.py, and somehow be transferred via update()?

            current = -10
            counter = 0
            # socketio.sleep(3)

            for i in range(0, int(RUNTIME_MAX / INTERVAL)):
                previous = current

                try:
                    if not VIRTUAL_MODBUS_DEBUG:
                        await self.update()
                    current = self._current_position

                except Exception as e:
                    error_count += 1
                    print(
                        f"Error count {error_count}. Error (Damper test, close, act position). OPEN. Have you connected the Modbus interface?"
                        + str(e)
                    )
                    error = "Close error, act pos" + str(e)
                    # damper_is_testing_temp = False
                    #   dampers_currently_testing.remove(modbus_address)
                    #   if True: #error_count >=3:
                    #       raise NameError('HiThere Close')

                print(
                    f"{self._modbus_address} - Current: {current}, Previous: {previous}"
                )
                if (
                    current == previous
                ):  # TO DO: Replace this clumsy end position detection with a better one
                    counter = counter + 1
                    print("break counter" + str(counter))
                    if counter > 3:
                        print("break realy")
                        counter = 0
                        break
                else:
                    print("reset counter to 0")
                    counter = 0
                print(
                    f"{self._modbus_address} - Current position: {current}, ({(current/100*90):.1f}°)"
                )
                position = round(current / 10000 * 90, 0)
                # data["position"] = position
                # emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON
                await asyncio.sleep(INTERVAL)
                # time.sleep(interval)

                # data["state"] = "Closed"
                runtime_final = round((time.time() - startTime), 1)
                print(f"Runtime Final: {runtime_final:.1f}s")
                # emit(damper_id, dumps(data), broadcast = True)  # dumps() converts the dictionnary to JSON

        except Exception as e:
            error_count += 1
            print(
                f"Error count {error_count}. Error (Damper test). Have you connected the Modbus interface?"
                + str(e)
            )
            if True:  # error_count >=3:
                self._currently_testing = False
                error = "Close error: " + str(e)
                print(f"Error: {error}")
                return
        await asyncio.sleep(
            5
        )  # TO DO: Remove this sleep in open position after debugging
        # socketio.sleep(5)  # TO DO: Remove this sleep in open position after debugging

        # data["state"] = "Closed"
        runtime = round((time.time() - startTime), 1)
        CRED = "\033[91m"
        CEND = "\033[0m"
        print(
            f"{CRED}Runtime, {self.name}, Target Position {target_position}: {runtime:.1f}s{CEND}"
        )

        return runtime


if __name__ == "__main__":
    print("hello from __main__")

    # hub = Hub("My Hub", "/serialbyid/bla")
    # hub.modbusAssignAddress(1)
    # hub.print_hub()

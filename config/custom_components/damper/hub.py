import time
import pickle
from logging import getLogger
from os.path import exists, join
from homeassistant.config import get_default_config_dir
from .const import (
    DOMAIN,
)  # might need to remove the . from .const, when running in homeassistant instead of command line

import json

### Imports from within this project:
from .modbusAutoAddress import *

# import modbusAutoAddress
from .modbusInstrument import ModbusInstrument

# DEBUGGING: python -m config.custom_components.damper.hub

# https://pythonexamples.org/python-pickle-class-object/
# https://stackoverflow.com/questions/44166092/why-is-pickle-not-serializing-my-array-of-classes
# https://github.com/shaftoe/home-assistant-custom-components/blob/4fc91d69cd9a99dc2d1facbab6aefa45832d7edc/spreaker2sonos.py

FILE = join(get_default_config_dir(), DOMAIN + ".pickle")
print(FILE)
# FILE = "./storage.pickle"


class Hub:
    # def __init__(self,damper):
    def __init__(self, name, com):
        # self.Main = None
        self._name = name
        self._com = com
        self._dampers = []

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
            newSlaveAddress,
            name,
            type_asn,
            manufacturing_date,
            factory_index,
            factory_seq_num,
        )
        self._dampers.append(damper)

    def modbusAssignAddress(self, nextAddress, name=None):

        VIRTUAL_MODBUS_DEBUG = True  ## used to test without a Modbus USB stick

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
                if VIRTUAL_MODBUS_DEBUG == False:
                    instrument = ModbusInstrument(newSlaveAddress)
                    type_asn = instrument.typeASN()
                    manufacturing_date = instrument.factoryDate()
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
        for damper in self._dampers:
            print(damper.__dict__)

    def store(self):

        # hubs = []
        # hubs.append(hub)
        # hubs = hub

        # """Store to file."""
        with open(FILE, "wb") as myfile:
            # pickle.dump({feed_url: timestamp}, myfile, pickle.HIGHEST_PROTOCOL)
            pickle.dump(hub, myfile, pickle.HIGHEST_PROTOCOL)
        myfile.close()

    def get_stored_data(self):
        """Return stored data."""
        if not exists(FILE):
            print("File doesn't exist")
            return {}
        print("Loading data")
        with open(FILE, "rb") as myfile:
            content = pickle.load(myfile)
        myfile.close()
        # self = content
        return content

    def print_dampers(self):
        for damper in self._dampers:
            print(damper.__dict__)
            # print(repr(damper))

    def print_damper(self, damper):
        print(damper.__dict__)


class Damper:
    _name: str
    _id: int
    _is_closed: bool
    _is_open: bool
    _modbus_address: int

    def __init__(
        self,
        modbus_address,
        name,
        type_asn,
        manufacturing_date,
        factory_index,
        factory_seq_num,
    ):
        self._modbus_address = modbus_address
        self._name = name
        self._type_asn = type_asn
        self._manufacturing_date = manufacturing_date
        self._factory_index = factory_index
        self._factory_seq_num = factory_seq_num

        self._id = 1  # TO DO: Remove or do a proper implementation
        self._is_closed = True
        self._is_open = False


if __name__ == "__main__":
    print("hello")

    hub = Hub("My Hub", "/serialbyid/bla")
    hub.modbusAssignAddress(1)
    hub.print_hub()

    # ## Generate & store data:
    # hub = Hub("My Hub", "/serialbyid/bla")
    # hub.print_hub()
    # hub.addNewDamperToDb(101, "Modbus 101", "GRA126", "31.12.2019", "A", "1234567890")
    # hub.addNewDamperToDb(102, "Modbus 102", "GRA126", "31.11.2019", "A", "1234567891")
    # hub.print_hub()
    # hub.store()

    # ## Load stored data:
    # hub = Hub("My Hub", "/serialbyid/bla")
    # hub = hub.get_stored_data()
    # hub.print_damper(hub._dampers[1])


# """
# Subscribe to feedreader events. If event is from Spreaker url.
# Parse the content and add the MP3 link to Sonos queue.
# """
# import pickle
# from logging import getLogger
# from os.path import exists, join

# from homeassistant.config import get_default_config_dir
# from homeassistant.components.feedreader import EVENT_FEEDREADER
# from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
# from homeassistant.components.media_player import (
#     SERVICE_PLAY_MEDIA, ATTR_MEDIA_ENQUEUE, ATTR_MEDIA_CONTENT_ID,
#     ATTR_MEDIA_CONTENT_TYPE)


# DOMAIN = 'spreaker2sonos'
# DEPENDENCIES = [MEDIA_PLAYER_DOMAIN]
# _LOGGER = getLogger(__name__)
# FILE = join(get_default_config_dir(), DOMAIN + '.pickle')
# DATE_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
# TIMESTAMP_ENTITY_KEY = 'published_parsed'


# def setup(hass, config):
#     """Setup the spreaker2sonos component."""
#     def get_stored_data():
#         """Return stored data."""
#         if not exists(FILE):
#             return {}
#         with open(FILE, 'rb') as myfile:
#             content = pickle.load(myfile)
#         myfile.close()
#         return content

#     def store_uri_timestamp(timestamp, feed_url):
#         """Store uri timestamp to file."""
#         with open(FILE, 'wb') as myfile:
#             pickle.dump({feed_url: timestamp}, myfile, pickle.HIGHEST_PROTOCOL)
#         myfile.close()

#     def get_uri_from_data(entry):
#         """Get mp3 link from feed entry data."""
#         for link in entry.links:
#             if link.get('type') == 'audio/mpeg':
#                 return link.get('href')

#     def get_new_uri_from_data(entry, feed_url):
#         """Return uri if does not match stored one."""
#         uri = get_uri_from_data(entry)
#         stored_entry_timestamp = get_stored_data().get(feed_url)
#         if (stored_entry_timestamp and
#                 entry.get(TIMESTAMP_ENTITY_KEY) <= stored_entry_timestamp):
#             _LOGGER.debug('URI %s already processed', uri)
#             return None
#         return uri

#     def parse_event(event):
#         """If event is a Spreaker feed url, parse and add it to queue."""
#         feed_url = event.data.get('feed_url', '')
#         if 'spreaker' in feed_url:
#             uri = get_new_uri_from_data(event.data, feed_url)

#             if uri:
#                 hass.services.call(MEDIA_PLAYER_DOMAIN,
#                                    SERVICE_PLAY_MEDIA,
#                                    {ATTR_MEDIA_CONTENT_ID: uri,
#                                     ATTR_MEDIA_CONTENT_TYPE: 'audio/mpeg',
#                                     ATTR_MEDIA_ENQUEUE: True})
#                 _LOGGER.info('Added URI "%s" to queue', uri)
#                 store_uri_timestamp(event.data.get(TIMESTAMP_ENTITY_KEY),
#                                     feed_url)

#     hass.bus.listen(EVENT_FEEDREADER, parse_event)
#     return True
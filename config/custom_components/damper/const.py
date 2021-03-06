"""Constants for the Coronavirus integration."""
# from coronavirus import DEFAULT_SOURCE

DOMAIN = "damper"
# OPTION_WORLDWIDE = "__worldwide"
ATTRIBUTION = f"Data provided by Matthias"
# ATTRIBUTION = f"Data provided by {DEFAULT_SOURCE.NAME}"

UNDO_UPDATE_LISTENER = "undo_update_listener"
HUB = "hub"

VIRTUAL_MODBUS_DEBUG = True
VIRTUAL_RUNTIME_OPEN = 60
VIRTUAL_RUNTIME_CLOSE = 20
VIRTUAL_RUNTIME_VAR_PERCENT = 15

RUNTIME_OPEN_MAX = 98
RUNTIME_CLOSE_MAX = 22
POWER_MAX = 3.0

TEST_CRITERIA = {
    "GMA161.1E/MO": {
        "RUNTIME_OPEN_MAX": 98,
        "RUNTIME_CLOSE_MAX": 101,
        "POWER_MAX": 3.0,
    },
    "GNA151.1E/T12M": {
        "RUNTIME_OPEN_MAX": 98,
        "RUNTIME_CLOSE_MAX": 22,
        "POWER_MAX": 3.0,
    },
    "GDB111.1E/MO": {"RUNTIME_OPEN_MAX": 98, "RUNTIME_CLOSE_MAX": 22, "POWER_MAX": 3.0},
    "GRA999-virtual": {
        "RUNTIME_OPEN_MAX": 71,
        "RUNTIME_CLOSE_MAX": 30,
        "POWER_MAX": 3.0,
    },
    "GRA126": {
        "RUNTIME_OPEN_MAX": 98,
        "RUNTIME_CLOSE_MAX": 22,
        "POWER_MAX": 3.0,
    },
}

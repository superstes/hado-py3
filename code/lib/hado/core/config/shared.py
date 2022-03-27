# config defaults, global vars, hardcoded stuff, setting validation

from hado.core.config.defaults import ENGINE as ENGINE_DEFAULTS


def init():
    # global variables shared across all modules
    global CONFIG_ENGINE
    global CONFIG_HA
    global CONFIG_LOADED
    CONFIG_HA = {}
    CONFIG_LOADED = {}
    CONFIG_ENGINE = ENGINE_DEFAULTS

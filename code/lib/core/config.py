engine_defaults = {
    'DEBUG': False,
    'TRACEBACK_LINES': 250,
    'SVC_INTERVAL_LOOP': 10,
    'SVC_INTERVAL_STATUS': 900,
    'PROCESS_TIMEOUT': 15,
    'DEFAULT_MONITORING_INTERVAL': 15,
    'DEFAULT_RESOURCE_VITAL': True,
    'DEFAULT_ACTION_FAILURE': 'demote',  # stop/demote/leave
    'DEFAULT_ACTION_SHUTDOWN': 'demote',
    'DEFAULT_MONITORING_VITAL': True,
    'DEFAULT_RESOURCE_MODE': 'shared',  # active-passive/active-active/standalone
    'DEFAULT_RESOURCE_MODE_PRIO': 1024,
}


def init():
    global CONFIG_ENGINE
    global CONFIG_HA
    CONFIG_HA = {}
    CONFIG_ENGINE = engine_defaults


HARDCODED = {
    'CONFIG_HA': '/etc/hado/config.yml',
    'CONFIG_ENGINE': '/etc/hado/engine.yml',
    'PATH_PLUGIN': '/var/local/lib/hado/plugin'
}

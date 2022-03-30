# hardcoded default values are collected here

ENGINE = {
    'DEBUG': False,
    'LOG_MODE': 'info',
    'PROCESS_TIMEOUT_ACTION': 30,
    'PROCESS_TIMEOUT_MONITORING': 5,
    'SYNC_LISTEN_PORT': 6185,
    'SYNC_LISTEN_IP': '0.0.0.0',
    'SYNC_PUBLIC_ALLOW_ANY': False,
    'SYNC_PUBLIC_ACCEPTLIST': [],
    'DEFAULT_MONITORING_INTERVAL': 15,
    'DEFAULT_RESOURCE_VITAL': True,
    'DEFAULT_ACTION_FAILURE': 'demote',
    'DEFAULT_ACTION_SHUTDOWN': 'demote',
    'DEFAULT_MONITORING_VITAL': True,
    'DEFAULT_RESOURCE_MODE': 'active-standby',
    'DEFAULT_RESOURCE_MODE_PRIO': 1024,
    'DEFAULT_PEER_SYNC_PORT': 6185,
    'TRACEBACK_LINES': 250,
    'SVC_INTERVAL_LOOP': 10,
    'SVC_INTERVAL_STATUS': 900,
}

HARDCODED = {
    'PATH_CONFIG': '/etc/hado',
    'PATH_PLUGIN': '/var/local/lib/hado/plugin',
    'FILE_CONFIG_HA': 'config.yml',
    'FILE_CONFIG_ENGINE': 'engine.yml',
    'FILE_CONFIG_ENGINE_DEFAULTS': 'engine.defaults.yml',
    'FILE_CONFIG_ENGINE_DEFAULTS_COMMENT': '---\n\n# These are the default values used by the HA-DO engine!\n\n',
    'MODE': {
        'VALID': [
            'active-standby', 'as', 'leader-worker', 'l2w', 'leader-leader', 'l2l',
            'standalone', 's',
        ],
        'ALIAS': {
            'as': 'active-standby',
            'l2w': 'leader-worker',
            'l2l': 'leader-leader',
            's': 'standalone',
        },
    },
    'ACTION': {
        'VALID': ['stop', 'demote', 'leave'],
    },
    'LOG_MODE': {
        'VALID': ['debug', 'info', 'warning', 'error'],
        'MAPPING': {'debug': 4, 'info': 3, 'warning': 2, 'error': 1},
        'MAPPING_REV': {4: 'DEBUG', 3: 'INFO', 2: 'WARNING', 1: 'ERROR'}
    },
    'REGEX_DNS': r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$)',
}

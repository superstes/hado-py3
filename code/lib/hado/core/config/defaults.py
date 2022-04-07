# hardcoded default values are collected here

_sync_user = 'hado'
_sync_pwd = 'kPw2HIFfQJ'

ENGINE = {
    # basic
    'DEBUG': False,
    'LOG_MODE': 'info',
    'TRACEBACK_LINES': 250,
    'SVC_INTERVAL_LOOP': 10,
    'SVC_INTERVAL_STATUS': 900,

    # plugins
    'PROCESS_TIMEOUT_ACTION': 30,
    'PROCESS_TIMEOUT_MONITORING': 5,
    'DEFAULT_ACTION_FAILURE': 'demote',
    'DEFAULT_ACTION_SHUTDOWN': 'demote',
    'DEFAULT_RESOURCE_MODE': 'active-standby',
    'DEFAULT_RESOURCE_MODE_PRIO': 1024,
    'DEFAULT_RESOURCE_VITAL': True,
    'DEFAULT_MONITORING_VITAL': False,
    'DEFAULT_MONITORING_WAIT': 15,

    # state sync/peers
    'PEER_HISTORY_MAX': 50,
    'CHECK_WAIT': 1,
    'DEFAULT_PEER_API_PORT': 6185,
    'DEFAULT_PEER_AUTH': True,
    'DEFAULT_PEER_SYNC_USER': _sync_user,
    'DEFAULT_PEER_SYNC_PWD': _sync_pwd,

    # api
    'API_LISTEN_PORT': 6185,
    'API_LISTEN_IP': '0.0.0.0',
    'API_PUBLIC_ALLOW_ANY': False,
    'API_PUBLIC_ACCEPTLIST': [],
    'API_POST_ACCEPT_NON_LOCAL': False,
    'API_POST_ACCEPTLIST': [],
    'API_AUTH': True,
    'API_SYNC_USER': _sync_user,
    'API_SYNC_PWD': _sync_pwd,
    'API_VIEW_USER': 'view',
    'API_VIEW_PWD': 'HA3752DO!',
    'API_SYNC_TIMEOUT': 2,
    'API_SYNC_SSL': False,
    'API_SYNC_SSL_VERIFY': False,
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
        'VALID': ['stop', 'demote', 'leave', 'fix', 'restart'],
    },
    'LOG_MODE': {
        'VALID': ['debug', 'info', 'warning', 'error'],
        'MAPPING': {'debug': 4, 'info': 3, 'warning': 2, 'error': 1},
        'MAPPING_REV': {4: 'DEBUG', 3: 'INFO', 2: 'WARNING', 1: 'ERROR'}
    },
    'REGEX_DNS': r'(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$)',
    'API_SYNC_PATH': '-',
    'API_SYNC_UA': 'HA-DO-SYNC',
}

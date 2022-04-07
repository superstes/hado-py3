from ipaddress import ip_address
from string import printable, ascii_letters, digits

from hado.core.config.defaults import HARDCODED

VALIDATION = {
    # basic
    'DEBUG': {'check': 'type', 'data': bool},
    'LOG_MODE': {'check': 'in', 'data': HARDCODED['LOG_MODE']['VALID']},
    'SVC_INTERVAL_LOOP': {'check': 'between', 'data': [0, 60 * 20 + 1]},
    'SVC_INTERVAL_STATUS': {'check': 'between', 'data': [0, 60 * 60 * 24 * 7 + 1]},
    'TRACEBACK_LINES': {'check': 'between', 'data': [0, 10_001]},

    # plugins
    'PROCESS_TIMEOUT_ACTION': {'check': 'between', 'data': [0, 60 * 20 + 1]},
    'PROCESS_TIMEOUT_MONITORING': {'check': 'between', 'data': [0, 61]},
    'DEFAULT_ACTION_FAILURE': {'check': 'in', 'data': HARDCODED['ACTION']['VALID']},
    'DEFAULT_ACTION_SHUTDOWN': {'check': 'in', 'data': HARDCODED['ACTION']['VALID']},
    'DEFAULT_RESOURCE_MODE': {'check': 'in', 'data': HARDCODED['MODE']['VALID']},
    'DEFAULT_RESOURCE_MODE_PRIO': {'check': 'between', 'data': [0, 2_049]},
    'DEFAULT_RESOURCE_VITAL': {'check': 'type', 'data': bool},
    'DEFAULT_MONITORING_VITAL': {'check': 'type', 'data': bool},
    'DEFAULT_MONITORING_WAIT': {'check': 'between', 'data': [0, 60 * 60 * 6 + 1]},

    # state sync/peers
    'API_LISTEN_PORT': {'check': 'between', 'data': [1_023, 49_152]},
    'CHECK_WAIT': {'check': 'between', 'data': [0, 60 * 60 + 1]},
    'DEFAULT_PEER_API_PORT': {'check': 'between', 'data': [1_023, 49_152]},
    'DEFAULT_PEER_AUTH': {'check': 'type', 'data': bool},
    'PEER_HISTORY_MAX': {'check': 'between', 'data': [0, 101]},
    'DEFAULT_PEER_SYNC_USER': {'check': 'user', 'data': None},
    'DEFAULT_PEER_SYNC_PWD': {'check': 'pwd', 'data': None},

    # api
    'API_AUTH': {'check': 'type', 'data': bool},
    'API_LISTEN_IP': {'check': 'ip-address', 'data': None},
    'API_SYNC_SSL': {'check': 'type', 'data': bool},
    'API_SYNC_SSL_VERIFY': {'check': 'type', 'data': bool},
    'API_PUBLIC_ALLOW_ANY': {'check': 'type', 'data': bool},
    'API_PUBLIC_ACCEPTLIST': {'check': 'type', 'data': list},
    'API_POST_ACCEPT_NON_LOCAL': {'check': 'type', 'data': bool},
    'API_POST_ACCEPTLIST': {'check': 'type', 'data': list},
    'API_SYNC_USER': {'check': 'user', 'data': None},
    'API_SYNC_PWD': {'check': 'pwd', 'data': None},
    'API_VIEW_USER': {'check': 'user', 'data': None},
    'API_VIEW_PWD': {'check': 'pwd', 'data': None},
    'API_SYNC_TIMEOUT': {'check': 'between', 'data': [0, 11]},
}

VALID_HC = {
    'pwd_min_len': 6,
    'pwd_max_len': 50,
    'pwd_chars': printable[:-6].replace(':', ''),
    'user_min_len': 1,
    'user_max_len': 20,
    'user_chars': ascii_letters + digits,
}

VALID_DESC = {
    'pwd': f"- length between {VALID_HC['pwd_min_len']} and {VALID_HC['pwd_max_len']}, "
           f"allowed characters: {VALID_HC['pwd_chars']}",
    'user': f"- length between {VALID_HC['user_min_len']} and {VALID_HC['user_max_len']}, "
            f"allowed characters: {VALID_HC['user_chars']}"
}


def validate(item: str, data: (int, str, bool) = None) -> (bool, str):
    # pylint: disable=R0911,R0912

    if item in VALIDATION:
        c = VALIDATION[item]['check']
        d = VALIDATION[item]['data']

        try:
            if data is None:
                _data, _desc = '', ''
                if d is not None:
                    _data = f' {d}'

                if c in VALID_DESC:
                    _desc = f" {VALID_DESC[c]}"

                return f"{c}{_data}{_desc}"

            elif c == 'in':
                if data in d:
                    return True

            elif c == 'between':
                if d[0] < int(data) < d[1]:
                    return True

            elif c == 'lower':
                if int(data) < d:
                    return True

            elif c == 'type':
                if isinstance(data, d):
                    return True

            elif c == 'ip-address':
                try:
                    ip_address(data)
                    return True

                except ValueError:
                    return False

            elif c == 'pwd':
                if VALID_HC['pwd_min_len'] <= len(data) <= VALID_HC['pwd_max_len'] and \
                        set(data).issubset(VALID_HC['pwd_chars']):
                    return True

            elif c == 'user':
                if VALID_HC['user_min_len'] <= len(data) <= VALID_HC['user_max_len'] and \
                        set(data).issubset(VALID_HC['user_chars']):
                    return True

        except ValueError:
            # if int-translation fails
            pass

    elif data is not None:
        return True

    elif data is None:
        return 'unconfigured'

    return False

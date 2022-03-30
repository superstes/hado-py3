from ipaddress import ip_address

from hado.core.config.defaults import HARDCODED

VALIDATION = {
    'DEFAULT_RESOURCE_MODE': {'check': 'in', 'data': HARDCODED['MODE']['VALID']},
    'DEFAULT_PEER_SYNC_PORT': {'check': 'between', 'data': [1023, 49152]},
    'PROCESS_TIMEOUT_ACTION': {'check': 'between', 'data': [0, 1801]},
    'PROCESS_TIMEOUT_MONITORING': {'check': 'between', 'data': [0, 61]},
    'DEFAULT_RESOURCE_MODE_PRIO': {'check': 'between', 'data': [0, 2049]},
    'DEFAULT_ACTION_FAILURE': {'check': 'in', 'data': HARDCODED['ACTION']['VALID']},
    'DEFAULT_ACTION_SHUTDOWN': {'check': 'in', 'data': HARDCODED['ACTION']['VALID']},
    'DEBUG': {'check': 'type', 'data': bool},
    'DEFAULT_RESOURCE_VITAL': {'check': 'type', 'data': bool},
    'DEFAULT_MONITORING_VITAL': {'check': 'type', 'data': bool},
    'SYNC_LISTEN_IP': {'check': 'ip-address', 'data': None},
    'SYNC_PUBLIC_ALLOW_ANY': {'check': 'type', 'data': bool},
    'SYNC_PUBLIC_ACCEPTLIST': {'check': 'type', 'data': list},
    'LOG_MODE': {'check': 'in', 'data': HARDCODED['LOG_MODE']['VALID']},
}


def validate(item: str, data: (int, str, bool)=None) -> (bool, str):
    # pylint: disable=R0911,R0912

    if item in VALIDATION:
        c = VALIDATION[item]['check']
        d = VALIDATION[item]['data']

        try:
            if data is None:
                if d is None:
                    return f"{c}"

                return f"{c} '{d}'"

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

        except ValueError:
            # if int-translation fails
            pass

    elif data is not None:
        return True

    elif data is None:
        return 'unconfigured'

    return False

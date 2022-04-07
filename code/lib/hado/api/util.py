from ipaddress import ip_address
from flask import request, jsonify, make_response

from hado.core.config import shared
from hado.util.debug import log

HTTP_STATI = {
    'NOT_FOUND': 404,
    'DENIED': 403,
    'NOT_IMPL': 501,
    'OK': 200,
}


def client_ip():
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)


def deny_public():
    # security measurement => don't allow access from public ips by default
    ip = client_ip()
    if not shared.CONFIG_ENGINE['API_PUBLIC_ALLOW_ANY']:
        if ip not in shared.CONFIG_ENGINE['API_PUBLIC_ACCEPTLIST'] and \
                ip_address(ip).is_global:
            log(
                f"Denying access to rest-server for ip '{ip}' "
                f"as the ip is public and not accept-listed!",
                lv=3
            )
            return json_error('DENIED')

    return None


def deny_nonlocal(ip):
    # security measurement => don't allow access from public ips by default
    if not shared.CONFIG_ENGINE['API_POST_ACCEPT_NON_LOCAL']:
        if not ip_address(ip).is_loopback:
            log(
                f"Denying post-access to rest-server for ip '{ip}' "
                f"as the ip is non-loopback!",
                lv=3
            )
            return json_error('DENIED')

    elif ip not in shared.CONFIG_ENGINE['API_POST_ACCEPTLIST']:
        log(
            f"Denying post-access to rest-server for ip '{ip}' "
            f"as the ip is non-loopback and not accept-listed!",
            lv=3
        )
        return json_error('DENIED')

    return None


def json_error(code: str):
    msg = {
        'DENIED': 'Access denied!',
        'NOT_FOUND': 'Requested resource or route does not exist!',
        'NOT_IMPL': 'Requested route is not yet implemented!',
    }
    return make_response(
        jsonify(message=msg[code]),
        HTTP_STATI[code]
    )

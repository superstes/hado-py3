from ipaddress import ip_address
from flask import request, abort

from hado.core.config.shared import CONFIG_ENGINE
from hado.util.debug import log

HTTP_STATI = {
    'NOT_FOUND': 404,
    'DENIED': 403,
    'NOT_IMPL': 501,
}


def client_ip():
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)


def deny_public():
    # security measurement => don't allow access from public ips by default
    ip = client_ip()
    if not CONFIG_ENGINE['API_PUBLIC_ALLOW_ANY']:
        if ip not in CONFIG_ENGINE['API_PUBLIC_ACCEPTLIST'] and \
                ip_address(ip).is_global:
            log(
                f"Denying access to rest-server for ip '{ip}' "
                f"as the ip is public and not accept-listed!",
                lv=3
            )
            abort(HTTP_STATI['DENIED'])


def deny_nonlocal(ip):
    # security measurement => don't allow access from public ips by default
    if not CONFIG_ENGINE['API_POST_ACCEPT_NON_LOCAL']:
        if not ip_address(ip).is_loopback:
            log(
                f"Denying post-access to rest-server for ip '{ip}' "
                f"as the ip is non-loopback!",
                lv=3
            )
            abort(HTTP_STATI['DENIED'])

    elif ip not in CONFIG_ENGINE['API_POST_ACCEPTLIST']:
        log(
            f"Denying post-access to rest-server for ip '{ip}' "
            f"as the ip is non-loopback and not accept-listed!",
            lv=3
        )
        abort(HTTP_STATI['DENIED'])

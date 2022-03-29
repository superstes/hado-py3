from ipaddress import ip_address
from re import match as regex_match
from socket import gethostbyname
from socket import error as resolve_error

from hado.core.config.defaults import HARDCODED


def valid_host(h: str) -> bool:
    valid = False
    try:
        ip_address(h)
        valid = True

    except ValueError:
        pass

    if regex_match(HARDCODED['REGEX_DNS'], h):
        try:
            # if hostname is valid dns and we can resolve it
            gethostbyname(h)
            valid = True

        except resolve_error:
            pass

    return valid

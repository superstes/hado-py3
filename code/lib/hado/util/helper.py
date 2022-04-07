import socket

from hado.util.debug import log


def value_exists(data: dict, key: str, vt=None) -> bool:
    if data is None or key not in data or not data[key]:
        return False

    if vt is not None and not isinstance(data[key], vt):
        log(f"Key '{key}' has not the expected type '{vt}'!", lv=2)
        log(f"Key '{key}' type '{type(data[key])}' != '{vt}' => data: '{data}'", lv=4)
        return False

    return True


def tcp_ping(host: str, port: int, timeout: float = 2) -> bool:
    tcp_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_stream.settimeout(timeout)
    ok = True

    try:
        tcp_stream.connect((host, port))
        tcp_stream.shutdown(socket.SHUT_RDWR)

    except (socket.timeout, socket.error,
            ConnectionError, ConnectionRefusedError,
            ConnectionResetError, ConnectionAbortedError):
        ok = False

    tcp_stream.close()

    return ok

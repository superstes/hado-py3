from os import getcwd

HTTP_CODES = {
    'NF': 404,
    'IM': 405,
    'D': 403,
    'NI': 501,
    'OK': 200,
}


def mock_paths(mocker) -> dict:
    from hado.core.config.defaults import HARDCODED
    h = HARDCODED.copy()
    h['PATH_CONFIG'] = f"{getcwd()}/../etc"
    h['PATH_PLUGIN'] = f"{getcwd()}/../plugin"
    mocker.patch('hado.core.config.defaults.HARDCODED', h)
    return h


def check_methods(p: str, c, u: str = 'get'):
    if u == 'post':
        rg = c.get(p)
        assert rg.status_code == HTTP_CODES['IM']

    elif u == 'get':
        rp = c.post(p)
        assert rp.status_code == HTTP_CODES['IM']

    rpu = c.put(p)
    assert rpu.status_code == HTTP_CODES['IM']
    rt = c.trace(p)
    assert rt.status_code == HTTP_CODES['IM']
    rd = c.delete(p)
    assert rd.status_code == HTTP_CODES['IM']
    rpa = c.patch(p)
    assert rpa.status_code == HTTP_CODES['IM']

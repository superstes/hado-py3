from re import match as regex_match

HTTP_CODES = {
    'NF': 404,
    'IM': 405,
    'D': 403,
    'NI': 501,
    'OK': 200,
}


def check_methods(p: str, c, u: str = 'get'):
    if u == 'post':
        rg = c.get(p)
        assert rg.status_code == HTTP_CODES['NF']
        # get has a catchall that returns 404

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


def match(m: str, i: str) -> bool:
    if regex_match(m, i.replace('\n', ' ')):
        return True

    return False


def capsys_error(i: str) -> bool:
    return match(m='.*ERROR.*', i=i)


def capsys_warning(i: str) -> bool:
    return match(m='.*WARNING.*', i=i)


def capsys_info(i: str) -> bool:
    return match(m='.*INFO.*', i=i)


def capsys_debug(i: str) -> bool:
    return match(m='.*DEBUG.*', i=i)

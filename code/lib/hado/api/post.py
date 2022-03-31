from typing import NoReturn
from flask import abort, Blueprint, Response

from hado.api.util import client_ip, deny_nonlocal, HTTP_STATI
from hado.util.debug import log

# pylint: disable=R1710

BOOL_MAPPING = {0: False, 1: True}
api_post = Blueprint('api_post', __name__)


@api_post.route('/c/m', defaults={'state': 1}, methods=['POST'])
@api_post.route('/c/m/<int:state>', methods=['POST'])
def post_maintenance(state: int) -> (Response, NoReturn):
    # todo: allowing admin to en- & disable maintenance mode
    ip = client_ip()
    deny_nonlocal(ip)
    s = BOOL_MAPPING[state]
    log(
        f"Received command 'maintenance => {s}' from client '{ip}'!",
        lv=2
    )
    abort(HTTP_STATI['NOT_IMPL'])


@api_post.route('/c/s', defaults={'state': 1}, methods=['POST'])
@api_post.route('/c/s/<int:state>', methods=['POST'])
def post_standby(state: int) -> (Response, NoReturn):
    # todo: allowing admin to en- & disable maintenance mode
    ip = client_ip()
    deny_nonlocal(ip)
    s = BOOL_MAPPING[state]
    log(
        f"Received command 'standby => {s}' from client '{ip}'!",
        lv=2
    )
    abort(HTTP_STATI['NOT_IMPL'])

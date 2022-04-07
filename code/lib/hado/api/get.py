from typing import NoReturn
from flask import jsonify, Blueprint, Response

from hado.core.config import shared
from hado.core.config.defaults import HARDCODED
from hado.api.util import deny_public, json_error
from hado.api.auth import auth, auth_optional

# pylint: disable=R1710

api_get = Blueprint('api_get', __name__)


@api_get.route('/', methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_whole() -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    _system = shared.CONFIG_LOADED['system'].stats
    _apps = {'apps': {app.name: app.stats for app in shared.CONFIG_LOADED['apps']}}
    _peers = {'peers': {peer.name: peer.stats_raw for peer in shared.CONFIG_LOADED['peers']}}
    return jsonify(_system | _apps | _peers)


@api_get.route(f"/{HARDCODED['API_SYNC_PATH']}", methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_sync() -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    _system = shared.CONFIG_LOADED['system'].stats
    _apps = {'apps': {app.name: app.stats for app in shared.CONFIG_LOADED['apps']}}
    return jsonify(_system | _apps)


@api_get.route('/s', methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_system() -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    return jsonify(shared.CONFIG_LOADED['system'].stats)


@api_get.route('/a/<string:app>', methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_app(app: str) -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    for a in shared.CONFIG_LOADED['apps']:
        if a.name == app:
            return jsonify(a.stats)

    return json_error('NOT_FOUND')


@api_get.route('/a/<string:app>/r/<string:res>', methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_resource(app: str, res: str) -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    for a in shared.CONFIG_LOADED['apps']:
        if a.name == app:
            for r in a.resources:
                if r.name == res:
                    return jsonify(r.stats)

    return json_error('NOT_FOUND')


@api_get.route('/a/<string:app>/m/<string:mon>', methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_monitoring(app: str, mon: str) -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    for a in shared.CONFIG_LOADED['apps']:
        if a.name == app:
            for m in a.monitoring:
                if m.name == mon:
                    return jsonify(m.stats)

    return json_error('NOT_FOUND')


@api_get.route('/d', methods=['GET'])
@auth.login_required(optional=auth_optional())
def get_debug() -> (Response, NoReturn):
    _d = deny_public()
    if _d is not None:
        return _d

    # todo: basic auth for debug config-dump
    return json_error('NOT_IMPL')

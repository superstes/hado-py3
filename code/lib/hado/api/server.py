from ipaddress import ip_address
from waitress import serve
from flask import Flask, request, abort
from flask_restful import Resource as RestResource
from flask_restful import Api as RestApi

from hado.core.config.shared import CONFIG_LOADED, CONFIG_ENGINE
from hado.api.stati import app_status, plugin_status, system_status
from hado.util.debug import log

# pylint: disable=R0201,R1710


def deny_public():
    # security measurement => don't allow access from public ips by default
    if not CONFIG_ENGINE['SYNC_PUBLIC_ALLOW_ANY']:
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

        if ip not in CONFIG_ENGINE['SYNC_PUBLIC_ACCEPTLIST'] and \
                ip_address(ip).is_global:
            log(
                f"Denying access to rest-server for ip '{ip}' "
                f"as the ip is public and not accept-listed!",
                lv=3
            )
            abort(403)


class Whole(RestResource):
    def get(self):
        deny_public()
        return {
            'system': system_status(),
            'apps': {a.name: app_status(a) for a in CONFIG_LOADED['apps']}
        }


class System(RestResource):
    def get(self):
        deny_public()
        return system_status()


class App(RestResource):
    def get(self, name: str):
        deny_public()
        for a in CONFIG_LOADED['apps']:
            if a.name == name:
                return app_status(a)

        abort(404)


class Res(RestResource):
    def get(self, app: str, res: str):
        deny_public()
        for a in CONFIG_LOADED['apps']:
            if a.name == app:
                for r in a.resources:
                    if r.name == res:
                        return plugin_status(r)

        abort(404)


class Mon(RestResource):
    def get(self, app: str, mon: str):
        deny_public()
        for a in CONFIG_LOADED['apps']:
            if a.name == app:
                for m in a.monitoring:
                    if m.name == mon:
                        return plugin_status(m)

        abort(404)


class RestServer:
    def __init__(self):
        self.flask_app = Flask(__name__)
        self.api = RestApi(self.flask_app)
        self.api.add_resource(Whole, '/')
        self.api.add_resource(System, '/s')
        self.api.add_resource(App, '/a/<string:name>')
        self.api.add_resource(Res, '/a/<string:app>/r/<string:res>')
        self.api.add_resource(Mon, '/a/<string:app>/m/<string:mon>')
        # self.api.add_resource(Debug, '/d')
        # todo: basic auth for debug config-dump
        self.ip = CONFIG_ENGINE['SYNC_LISTEN_IP']
        self.port = CONFIG_ENGINE['SYNC_LISTEN_PORT']

    def start(self):
        # pylint: disable=W0703
        log(f'Starting rest-server on port {self.port}.', lv=3)
        try:
            serve(
                app=self.flask_app,
                host=self.ip,
                port=self.port,
            )

        except Exception as e:
            log(f"Rest-server died with error: '{e}'!")

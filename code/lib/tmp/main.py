import yaml
from flask import Flask
from flask_restful import Resource as RestResource
from flask_restful import Api as RestApi

rest_app = Flask(__name__)
rest_api = RestApi(rest_app)

config = {
    'system': {
        'monitoring': {  # testing system health and availability of external resources that affect all apps
            'ping_gw': {
                'plugin': 'ping',
                'plugin_args': '-t=10.1.5.1 -s=10.1.5.100',
                'interval': 10,
            },
        },
    },
    'apps': {
        'fancy': {
            'description': 'Such a fancy app',
            'status': 0,
            'health': 66,  # percentage of resources available
            'on_failure': 'stop',  # if a vital part of the application breaks; stop all other parts on this server
            # stop/leave
            'resources': {
                'background-task': {
                    'plugin': 'systemd',
                    'plugin_args': '-s=bgtasks.service',
                    'mode': 'standalone',  # default
                    'vital': False,  # default
                    'status': 1,
                },
                'share': {
                    'plugin': 'samba_share',
                    'plugin_args': '-s=fancy',
                    'vital': True,  # the app will be marked as failed if a vital part is down
                    'status': 0,
                },
                'database': {
                    'plugin': 'mysql',
                    'plugin_args': '-i=fancyDB',
                    'mode': 'cluster',
                    'vital': True,
                    'status': 1,
                },
                'some_ip': {
                    'plugin': 'ipaddr',
                    'plugin_args': '-i=10.1.5.4 -d=eno1',
                    'vital': True,
                    'status': 1,
                },
            },
            'monitoring': {  # testing system health and availability of external resources that only affect this app
                'other_service': {
                    'plugin': 'port',  # checking if a port is reachable
                    'plugin_args': '-t=11.0.9.5 -p=8080 -s=10.1.5.100',
                    'interval': 60,
                },
            },
        },
    },
}

with open('test.yml', 'w') as cnf:
    cnf.write(yaml.dump(config))


class App(RestResource):
    def get(self, name: str):
        app = config['apps'][name] if name in config['apps'] else {}

        return app


class Res(RestResource):
    def get(self, app: str, res: str):
        _app = config['apps'][app]['resources'] if app in config['apps'] else {}

        return _app[res] if res in _app else {}


rest_api.add_resource(App, '/a/<string:name>')
rest_api.add_resource(Res, '/a/<string:app>/<string:res>')

rest_app.run(port=2000, debug=False)

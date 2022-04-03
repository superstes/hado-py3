# Test functionality of the app-object

from re import match as regex_match

from hado.core.app import App

from .util import capsys_warning


class PseudoPlugin:
    ACTIONS = {
        'check': 'WHIIII_CHECK',
    }

    def __init__(self, name: str, config: dict):
        self.name = name
        self.status = True
        self.vital = config['vital'] if 'vital' in config else True

    def action(self, a: str):
        try:
            print(f"{self.name}_{self.ACTIONS[a]}")

        except KeyError:
            pass


class PseudoResource(PseudoPlugin):
    ACTIONS = {
        'start': 'WHUPII_START',
        'stop': 'WHUPSII_STOP',
        'init': 'WHUPAA_INIT',
        'demote': 'WHUPO_DEMOTE',
        'promote': 'WHUPNN_PROMOTE',
        'fix': 'WHAAA_FIX',
    }

    def __init__(self, name: str, config: dict, sequence: int):
        super(PseudoResource, self).__init__(name=name, config=config)
        self.sequence = sequence
        self.on_failure = config['on_failure'] if 'on_failure' in config else None
        self.on_shutdown = config['on_shutdown'] if 'on_shutdown' in config else None
        self.mode = config['mode'] if 'mode' in config else 'active-standby'


def check_action(c, a: str, i: PseudoPlugin, n: bool = False):
    stdout, _ = c.readouterr()
    s = stdout.replace('\n', ' ')
    if a in i.ACTIONS:
        if n:
            assert not regex_match(f".*{i.name}_{i.ACTIONS[a]}.*", s)

        else:
            assert regex_match(f".*{i.name}_{i.ACTIONS[a]}.*", s)


class TestApp:
    def test_app_health(self, mocker):
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)

        app = {
            'peers': [],
            'resources': {
                'testRes1': {},
                'testRes2': {},
            },
            'monitoring': {
                'testMon1': {},
            }
        }

        a = App(name='APP-a', app=app)

        # if not initialized
        assert a.health == 0.0
        assert a.resource_health == 0.0
        assert a.monitoring_health == 0.0
        assert not a.status
        assert a.failed

        a.init_resources()
        assert a.health == 100.0
        assert a.resource_health == 100.0
        assert a.monitoring_health == 100.0
        assert a.status
        assert not a.failed

    def test_app_health_vitality(self, mocker):
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)

        app = {
            'peers': [],
            'resources': {
                'testRes1': {'vital': False},
            },
            'monitoring': {
                'testMon1': {'vital': False},
            }
        }

        a = App(name='APP-b', app=app)
        a.init_resources()

        # no vital
        assert a.health == 100.0
        assert a.resource_health == 100.0
        assert a.monitoring_health == 100.0
        assert a.status

        a.resources[0].status = False
        assert a.resource_health == 0.0
        assert a.status

        a.monitoring[0].status = False
        assert a.monitoring_health == 0.0
        assert a.status

        # reset
        a.resources[0].status = True
        a.monitoring[0].status = True

        # resource is only vital
        a.resources[0].vital = True
        assert a.status
        a.resources[0].status = False
        assert not a.status

        # reset
        a.resources[0].status = True
        a.resources[0].vital = False

        # monitoring is only vital
        a.monitoring[0].vital = True
        assert a.status
        a.monitoring[0].status = False
        assert not a.status

        # reset
        a.monitoring[0].status = True
        a.monitoring[0].vital = False

        # both vital
        a.resources[0].vital = True
        a.monitoring[0].vital = True
        assert a.status

        a.monitoring[0].status = False
        assert not a.status
        a.resources[0].status = False
        assert not a.status

    def test_app_action(self, mocker, capsys):
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)

        app = {
            'peers': [],
            'resources': {
                'testRes1': {},
            },
            'monitoring': {
                'testMon1': {},
            }
        }

        a = App(name='APP-c', app=app)
        a.init_resources()

        res = a.resources[0]
        mon = a.monitoring[0]

        # all resource actions
        check_action(c=capsys, a='init', i=res)
        a.action('start')
        check_action(c=capsys, a='start', i=res)
        a.action('stop')
        check_action(c=capsys, a='stop', i=res)
        a.action('promote')
        check_action(c=capsys, a='promote', i=res)
        a.action('demote')
        check_action(c=capsys, a='demote', i=res)
        a.action('fix')
        check_action(c=capsys, a='fix', i=res)

        # monitoring action
        a.action('check')
        check_action(c=capsys, a='check', i=mon)

        # unsupported action should trigger warning
        a.action('unsupported')
        stdout, _ = capsys.readouterr()
        assert capsys_warning(stdout)

    def test_app_on_failure(self, mocker, capsys):
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)

        # default failure
        app = {
            'peers': [],
            'resources': {
                'testRes1': {},
            },
        }

        a = App(name='APP-d-a', app=app)
        a.init_resources()
        res = a.resources[0]
        check_action(c=capsys, a='init', i=res)
        a.failure()
        check_action(c=capsys, a='demote', i=res)
        del a

        # resource action override
        app = {
            'peers': [],
            'resources': {
                'testRes1': {'on_failure': 'stop'},
            },
        }

        b = App(name='APP-d-b', app=app)
        b.init_resources()
        res = b.resources[0]
        check_action(c=capsys, a='init', i=res)
        b.failure()
        check_action(c=capsys, a='stop', i=res)
        del b

        # skip on action = leave
        app = {
            'peers': [],
            'resources': {
                'testRes1': {'on_failure': 'leave'},
            },
        }

        c = App(name='APP-d-c', app=app)
        c.init_resources()
        res = c.resources[0]
        check_action(c=capsys, a='init', i=res)
        c.failure()
        check_action(c=capsys, a='start', i=res, n=True)
        check_action(c=capsys, a='stop', i=res, n=True)
        check_action(c=capsys, a='init', i=res, n=True)
        check_action(c=capsys, a='demote', i=res, n=True)
        check_action(c=capsys, a='promote', i=res, n=True)
        del c

    def test_app_on_shutdown(self, mocker, capsys):
        mocker.patch('hado.core.app.Monitoring', PseudoPlugin)
        mocker.patch('hado.core.app.Resource', PseudoResource)

        # default failure
        app = {
            'peers': [],
            'resources': {
                'testRes1': {},
            },
        }

        a = App(name='APP-e-a', app=app)
        a.init_resources()
        res = a.resources[0]
        check_action(c=capsys, a='init', i=res)
        a.shutdown()
        check_action(c=capsys, a='demote', i=res)
        del a

        # resource action override
        app = {
            'peers': [],
            'resources': {
                'testRes1': {'on_shutdown': 'stop'},
            },
        }

        b = App(name='APP-e-b', app=app)
        b.init_resources()
        res = b.resources[0]
        check_action(c=capsys, a='init', i=res)
        b.shutdown()
        check_action(c=capsys, a='stop', i=res)
        del b

        # skip on action = leave
        app = {
            'peers': [],
            'resources': {
                'testRes1': {'on_shutdown': 'leave'},
            },
        }

        c = App(name='APP-e-c', app=app)
        c.init_resources()
        res = c.resources[0]
        check_action(c=capsys, a='init', i=res)
        c.shutdown()
        check_action(c=capsys, a='start', i=res, n=True)
        check_action(c=capsys, a='stop', i=res, n=True)
        check_action(c=capsys, a='init', i=res, n=True)
        check_action(c=capsys, a='demote', i=res, n=True)
        check_action(c=capsys, a='promote', i=res, n=True)
        del c

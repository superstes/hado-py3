# Test functionality of the plugin-object

from os import getcwd
from re import match as regex_match
import pytest

from hado.core.plugin.driver import Plugin, PluginType

from .util import capsys_debug, capsys_warning, capsys_info


def mock_paths(mocker) -> dict:
    from hado.core.config.defaults import HARDCODED
    h = HARDCODED.copy()
    h['PATH_PLUGIN'] = f"{getcwd()}/../test/data/plugin"
    mocker.patch('hado.core.plugin.driver.HARDCODED', h)
    return h


class TestPlugins:
    ACTIONS = {
        'r': ['start', 'stop', 'active', 'other', 'init', 'fix', 'promote', 'demote', 'leader'],
        'm': ['check'],
    }

    def test_plugin_init(self, mocker):
        with pytest.raises(NotADirectoryError):
            Plugin(
                plugin_type=PluginType.resource,
                name='doesNotExist',
                args=[],
            )

        mock_paths(mocker)
        assert Plugin(
            plugin_type=PluginType.resource,
            name='3a',
            args=[],
        )._get_cmds() == self.ACTIONS['r']

        assert Plugin(
            plugin_type=PluginType.monitoring,
            name='3a',
            args=[],
        )._get_cmds() == self.ACTIONS['m']

    def test_plugin_cmd_support(self, mocker, capsys):
        from hado.core.config.shared import CONFIG_ENGINE
        CONFIG_ENGINE['DEBUG'] = True
        mock_paths(mocker)

        pr = Plugin(
            plugin_type=PluginType.resource,
            name='3a',
            args=[],
        )
        pm = Plugin(
            plugin_type=PluginType.monitoring,
            name='3a',
            args=[],
        )

        assert pr._get_cmds() == self.ACTIONS['r']
        for c in self.ACTIONS['r']:
            assert pr._check_cmd_support(c)

        assert pm._get_cmds() == self.ACTIONS['m']
        for c in self.ACTIONS['m']:
            assert pm._check_cmd_support(c)

        with pytest.raises(ValueError):
            pm._check_cmd_support(t='unsupported', s=1)

        _, _ = capsys.readouterr()
        pm._check_cmd_support(t='unsupported', s=2)
        stdout, _ = capsys.readouterr()
        assert capsys_warning(stdout)
        pm._check_cmd_support(t='unsupported', s=3)
        stdout, _ = capsys.readouterr()
        assert capsys_debug(stdout)
        CONFIG_ENGINE['DEBUG'] = False

    def test_plugin_cmd_build_base(self, mocker, capsys):
        # NOTE: not testing unsupported commands as they get filtered before
        h = mock_paths(mocker)
        start_cmd = ['bash', h['PATH_PLUGIN'] + '/resource/3a/generic.sh', 'start']

        p = Plugin(
            plugin_type=PluginType.resource,
            name='3a',
            args=[],
        )

        assert p._check_build_cmd(t='start') == start_cmd

        # testing info when plugin uses 'exec' string instead of list
        _, _ = capsys.readouterr()
        with open('/tmp/test.fix.sh', 'w+') as f:
            f.write('test')

        p._check_build_cmd(t='fix')
        stdout, _ = capsys.readouterr()
        assert capsys_info(stdout)

        # files do not exist
        with pytest.raises(FileNotFoundError):
            p._check_build_cmd(t='init')

        with pytest.raises(FileNotFoundError):
            p._check_build_cmd(t='leader')

    def test_plugin_cmd_build(self, mocker, capsys):
        h = mock_paths(mocker)
        from hado.core.config.shared import CONFIG_ENGINE
        CONFIG_ENGINE['DEBUG'] = True

        start_cmd = ['bash', h['PATH_PLUGIN'] + '/resource/3a/generic.sh', 'start']
        arg = 'test'

        p = Plugin(
            plugin_type=PluginType.resource,
            name='3a',
            args=[arg],
        )

        assert p._get_cmd(t='start') == (start_cmd + [arg])
        stdout, _ = capsys.readouterr()
        assert capsys_debug(stdout)
        CONFIG_ENGINE['DEBUG'] = False

        # too few arguments supplied
        with pytest.raises(ValueError):
            p._get_cmd(t='stop')

    def test_plugin_exec(self, mocker, capsys):
        mock_paths(mocker)

        r3b = Plugin(
            plugin_type=PluginType.resource,
            name='3b',
            args=[],
        )

        _, _ = capsys.readouterr()

        assert r3b.start()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3b.stop()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert not regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3b.promote()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3b.demote()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert not regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3b.init()
        assert r3b.fix()
        assert r3b.is_other
        assert r3b.is_leader
        assert r3b.is_active

        del r3b

        r3c = Plugin(
            plugin_type=PluginType.resource,
            name='3c',
            args=[],
        )

        _, _ = capsys.readouterr()

        assert r3c.start()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert not regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3c.stop()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3c.promote()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert not regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3c.demote()
        stdout, _ = capsys.readouterr()
        capsys_warning(stdout)
        assert regex_match(f'.*not executing.*', stdout.replace('\n', ' '))

        assert r3c.init()
        assert r3c.fix()
        assert not r3c.is_other
        assert not r3c.is_leader
        assert not r3c.is_active

        del r3c

    def test_plugin_exec_ni(self, mocker):
        mock_paths(mocker)

        r3d = Plugin(  # all results = 1
            plugin_type=PluginType.resource,
            name='3d',
            args=[],
        )

        # check for not implemented actions
        assert not r3d.init()
        assert not r3d.fix()
        assert not r3d.promote()
        assert not r3d.demote()
        del r3d

        r3e = Plugin(
            plugin_type=PluginType.resource,
            name='3e',
            args=[],
        )
        m3b = Plugin(
            plugin_type=PluginType.monitoring,
            name='3b',
            args=[],
        )

        # start/stop/check need to be implemented
        with pytest.raises(ValueError):
            r3e.start()

        with pytest.raises(ValueError):
            r3e.stop()

        with pytest.raises(ValueError):
            m3b.check()

        del r3e
        del m3b
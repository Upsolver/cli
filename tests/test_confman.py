from pathlib import Path

import pytest
from yarl import URL

from cli.config import Config, ConfigurationManager, LogLvl, Options, OutputFmt, Profile
from cli.errors import ConfigReadFail

default_profile = Profile(
    name='default',
    token='stamtoken',
    base_url=URL('https://stambaseurl'),
    output=OutputFmt.JSON,
)

basic_config = '''[profile]
token = stamtoken
base_url = stambaseurl
output = JSON
'''


def test_creates_dir_hier(tmp_path: Path):
    p = tmp_path / 'doesntexists' / 'config'
    assert not p.exists()
    ConfigurationManager(p)
    assert p.exists()


def test_creates_file(tmp_path: Path):
    p = tmp_path / 'doesntexist.conf'
    assert not p.exists()
    ConfigurationManager(p)
    assert p.exists()


def test_fail_parse(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write('123456')

    with pytest.raises(ConfigReadFail) as ex:
        ConfigurationManager(conf_path)
    exstr = str(ex.value)
    assert 'Failed to read' in exstr
    assert 'File contains no section headers' in exstr


def test_simple(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config)

    confm = ConfigurationManager(conf_path)
    assert confm.conf == Config(
        active_profile=default_profile,
        profiles=[default_profile],
        options=Options(ConfigurationManager.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )


def test_nonexistent_profile_is_ok(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config)

    # TODO profiles contains only the default profile... it's kinda strange that
    #   the active profile doesnt exist, even within config repr itself... although correct:
    #   all actions that depend on the non-existent profile will use default config values
    #   and in-case of an update to the profile it will actually be written...

    confm = ConfigurationManager(conf_path, profile='doesntexist')
    assert confm.conf == Config(
        active_profile=Profile(name='doesntexist', token=None, base_url=None),
        profiles=[default_profile],
        options=Options(ConfigurationManager.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )


def test_setting_option(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config + '''\n[options]\nlog_level=INFO\n''')

    confm = ConfigurationManager(conf_path)
    assert confm.conf == Config(
        active_profile=default_profile,
        profiles=[default_profile],
        options=Options(ConfigurationManager.CLI_DEFAULT_LOG_PATH, LogLvl.INFO),
        debug=False,
    )


def test_active_profile(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config + '''\n[profile.kool]\ntoken=stam\nbase_url=stam''')

    active_profile = Profile(name='kool', token='stam', base_url=URL('https://stam'))
    confm = ConfigurationManager(conf_path, profile='kool')
    assert confm.conf == Config(
        active_profile=active_profile,
        profiles=[default_profile, active_profile],
        options=Options(ConfigurationManager.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )


def test_profile_update(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config + '''\n[profile.kool]\ntoken=stam\nbase_url=stam''')

    active_profile = Profile(name='kool', token='stam', base_url=URL('https://stam'))
    confm = ConfigurationManager(conf_path, profile='kool')
    assert confm.conf == Config(
        active_profile=active_profile,
        profiles=[default_profile, active_profile],
        options=Options(ConfigurationManager.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )

    new_active_profile = Profile(name='kool', token='stam2', base_url=URL('https://stam2'))
    new_conf = confm.update_profile(new_active_profile)
    assert new_conf.active_profile == new_active_profile
    assert new_active_profile in new_conf.profiles


def test_option_log_file_path():
    # overwrite log file path in [options] section of config file and see that it takes effect
    pass


def test_debug_flag():
    pass

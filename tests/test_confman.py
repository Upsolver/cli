from pathlib import Path

import pytest

from cli.config import Config, ConfMan, LogLvl, Options, OutputFmt, Profile
from cli.errors import ConfigReadFail

default_profile = Profile(
    name='default',
    token='stamtoken',
    base_url='stambaseurl',
    output=OutputFmt.JSON,
)

basic_config = '''[profile]
token = stamtoken
base_url = stambaseurl
output = JSON
'''


def test_bad_path(tmp_path: Path):
    with pytest.raises(ConfigReadFail) as ex:
        ConfMan(Path('/simply/does/not/exist'))
    exstr = str(ex.value)
    assert 'Failed' in exstr
    assert 'read' in exstr
    assert '/simply/does/not/exist' in exstr


def test_path_exists_but_not_file(tmp_path: Path):
    confman = ConfMan(tmp_path / 'doesntexist.conf')
    assert confman.conf.active_profile.name == 'default'


def test_fail_parse(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write('123456')

    with pytest.raises(ConfigReadFail) as ex:
        ConfMan(conf_path)
    exstr = str(ex.value)
    assert 'Failed to read' in exstr
    assert 'File contains no section headers' in exstr


def test_simple(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config)

    confm = ConfMan(conf_path)
    assert confm.conf == Config(
        active_profile=default_profile,
        profiles=[default_profile],
        options=Options(ConfMan.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
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

    confm = ConfMan(conf_path, profile='doesntexist')
    assert confm.conf == Config(
        active_profile=Profile(name='doesntexist', token=None, base_url=None),
        profiles=[default_profile],
        options=Options(ConfMan.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )


def test_setting_option(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config + '''\n[options]\nlog_level=INFO\n''')

    confm = ConfMan(conf_path)
    assert confm.conf == Config(
        active_profile=default_profile,
        profiles=[default_profile],
        options=Options(ConfMan.CLI_DEFAULT_LOG_PATH, LogLvl.INFO),
        debug=False,
    )


def test_active_profile(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config + '''\n[profile.kool]\ntoken=stam\nbase_url=stam''')

    active_profile = Profile(name='kool', token='stam', base_url='stam')
    confm = ConfMan(conf_path, profile='kool')
    assert confm.conf == Config(
        active_profile=active_profile,
        profiles=[default_profile, active_profile],
        options=Options(ConfMan.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )


def test_profile_update(tmp_path: Path):
    conf_path = tmp_path / 'stam.conf'
    with open(conf_path, 'w') as conf_f:
        conf_f.write(basic_config + '''\n[profile.kool]\ntoken=stam\nbase_url=stam''')

    active_profile = Profile(name='kool', token='stam', base_url='stam')
    confm = ConfMan(conf_path, profile='kool')
    assert confm.conf == Config(
        active_profile=active_profile,
        profiles=[default_profile, active_profile],
        options=Options(ConfMan.CLI_DEFAULT_LOG_PATH, LogLvl.CRITICAL),
        debug=False,
    )

    new_active_profile = Profile(name='kool', token='stam2', base_url='stam2')
    new_conf = confm.update_profile(new_active_profile)
    assert new_conf.active_profile == new_active_profile
    assert new_active_profile in new_conf.profiles


def test_option_log_file_path():
    # overwrite log file path in [options] section of config file and see that it takes effect
    pass


def test_debug_flag():
    pass

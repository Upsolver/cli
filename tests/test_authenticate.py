from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
from pytest_mock import MockerFixture

from cli.commands.authenticate import authenticate
from cli.commands.context import CliContext
from cli.config import ConfMan, ProfileAuthSettings, get_auth_settings

auth_settings = ProfileAuthSettings(token='token1234', base_url='base_url')


def test_auth_settings_saved(mocker: MockerFixture, tmp_path: Path) -> None:
    api = mocker.MagicMock()
    api.authenticate = mocker.MagicMock(
        return_value=auth_settings
    )

    ctx = CliContext(ConfMan(tmp_path / 'conf'))
    runner = CliRunner()
    with patch.object(ctx, 'upsolver_api', return_value=api) as upsolver_api_mock:
        runner.invoke(authenticate, ['-e', 'email', '-p', 'password'], obj=ctx)
        upsolver_api_mock.assert_called_with(None)  # creation of api w/ default auth_base_url
        api.authenticate.assert_called_once_with('email', 'password')  # auth call is made
        assert get_auth_settings(ctx.confman.conf.active_profile) == auth_settings  # settings are saved


def test_custom_auth_base_url(mocker: MockerFixture, tmp_path: Path) -> None:
    api = mocker.MagicMock()
    api.authenticate = mocker.MagicMock(
        return_value=auth_settings
    )

    ctx = CliContext(ConfMan(tmp_path / 'conf'))
    with patch.object(ctx, 'upsolver_api', return_value=api) as upsolver_api_mock:
        CliRunner().invoke(
            authenticate,
            ['-e', 'email', '-p', 'password', '-u', 'custom_auth_base_url'],
            obj=ctx
        )

        upsolver_api_mock.assert_called_with('custom_auth_base_url')


def test_token_is_printed(mocker: MockerFixture, tmp_path: Path) -> None:
    api = mocker.MagicMock()
    api.authenticate = mocker.MagicMock(
        return_value=auth_settings
    )

    ctx = CliContext(ConfMan(tmp_path / 'conf'))
    runner = CliRunner()
    with patch.object(ctx, 'upsolver_api', return_value=api):
        result = runner.invoke(authenticate, ['-e', 'email', '-p', 'password'], obj=ctx)
        assert 'Successful' in result.stdout
        assert auth_settings.token in result.stdout


def test_api_err(mocker: MockerFixture, tmp_path: Path) -> None:
    api = mocker.MagicMock()
    api.authenticate.side_effect = Exception('bad things')

    ctx = CliContext(ConfMan(tmp_path / 'conf'))
    runner = CliRunner()
    with patch.object(ctx, 'upsolver_api', return_value=api):
        conf_before = ctx.confman.conf
        result = runner.invoke(authenticate, ['-e', 'email', '-p', 'password'], obj=ctx)
        assert ctx.confman.conf == conf_before
        assert str(result.exception) == str(api.authenticate.side_effect)

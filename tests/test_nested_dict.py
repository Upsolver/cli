import pytest

from cli.utils import NestedDictAccessor


def test_simple_access() -> None:
    assert NestedDictAccessor({'a': 1})['a'] == 1


def test_nested_access() -> None:
    assert NestedDictAccessor({'a': {'b': {'c': 1}}})['a.b.c'] == 1


def test_bad_path() -> None:
    with pytest.raises(KeyError) as err:
        _ = NestedDictAccessor({'a': {'b': {'c': 1}}})['a.x.c']

    assert 'Missing a.x.c' in str(err.value)

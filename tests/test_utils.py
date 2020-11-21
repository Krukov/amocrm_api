import pytest

from amocrm.v2.model import _get_container_by_path


@pytest.mark.parametrize(
    ("path", "data", "expect"),
    [
        (["name"], {"name": "test"}, {"name": "test"}),
        (["name"], {"name": "test", "value": "no"}, {"name": "test"}),
        (["name", "value"], {"name": {"value": "test"}}, {"name": {"value": "test"}}),
        (["name", "value"], {"name": {"value": "test", "second": "No"}}, {"name": {"value": "test"}}),
    ],
)
def test_container(path, data, expect):
    assert _get_container_by_path(path, data) == expect

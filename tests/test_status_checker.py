import ast

import pytest

from flake8_drf.plugin import Plugin


@pytest.fixture
def views_code():
    with open("tests/views.py", "r") as file:
        code = file.read()

    return code


def test_status_codes_checker(views_code: str):
    tree = ast.parse(views_code)
    plugin = Plugin(tree)

    errors = list(plugin.run())

    assert len(errors) == 2

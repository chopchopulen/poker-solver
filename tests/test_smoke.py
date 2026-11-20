"""Smoke test: every package imports."""
import importlib

import pytest

PACKAGES = ["games", "solvers", "eval", "agents", "play", "tests", "scripts"]


@pytest.mark.parametrize("name", PACKAGES)
def test_package_imports(name):
    assert importlib.import_module(name) is not None

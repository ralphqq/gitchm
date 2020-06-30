"""
Test fixtures used in the CLI tests

Fixtures:
    mocked_item_func()
    item_ops_factory()
"""
from unittest.mock import MagicMock

import pytest

from app.cli import ItemParser
from tests.utils import ITEM_OPS_RETURN_VALUE


@pytest.fixture
def mocked_item_func():
    return MagicMock(return_value=ITEM_OPS_RETURN_VALUE)


@pytest.fixture
def item_ops_factory():
    """Wraps function for creating list of validators/transformers."""

    def _create(side_effect=None, params=None):
        m = MagicMock(side_effect=side_effect)
        return [
            ItemParser(
                apply=m,
                params=params,
                error_msg=str(i)
            )
            for i in range(len(side_effect))
        ]
    return _create

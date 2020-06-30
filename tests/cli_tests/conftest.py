"""
Test fixtures used in the CLI tests

Fixtures:
    mocked_item_func()
    item_parsers()
    default_item()
    required_item()
"""
from unittest.mock import MagicMock

import pytest

from app.cli import ItemParser, PromptItem, PromptUI
from tests.utils import ITEM_OPS_RETURN_VALUE


@pytest.fixture
def mocked_item_func():
    return MagicMock(return_value=ITEM_OPS_RETURN_VALUE)


@pytest.fixture
def item_parsers():
    """Wraps function for creating list of validators/transformers."""

    def _create(side_effect=None, params=None):
        m = MagicMock(side_effect=side_effect)
        return [
            ItemParser(
                apply=m,
                params=params[i],
                error_msg=str(i)
            )
            for i in range(len(side_effect))
        ]
    return _create


@pytest.fixture
def default_item():
    item = PromptItem(
        name='default_item',
        message='Optional field',
    )
    return item

@pytest.fixture
def required_item():
    item = PromptItem(
        name='required_item',
        message='Required field',
        is_required=True
    )
    return item


@pytest.fixture
def prompt_items():
    pass

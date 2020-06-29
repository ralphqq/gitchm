"""
Test fixtures used in the CLI tests

Fixtures:
    mocked_item_func()
"""
from unittest.mock import MagicMock

import pytest

from tests.utils import ITEM_OPS_RETURN_VALUE


@pytest.fixture
def mocked_item_func():
    return MagicMock(return_value=ITEM_OPS_RETURN_VALUE)

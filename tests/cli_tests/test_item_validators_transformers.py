"""
Unit tests for item validators and transformers

Classes:
    TestValidatorTransformer

"""
import pytest

from app.cli import ItemParser
from tests.utils import ITEM_OPS_RETURN_VALUE


PARAMS = {'a': 1, 'b': 2}
ERROR_MSG = 'Error'


class TestValidatorTransformer:

    def test_creation_with_values(self, mocked_item_func):
        ops = ItemParser(mocked_item_func, params=PARAMS, error_msg=ERROR_MSG)
        assert ops
        assert ops.params == PARAMS
        assert ops.error_msg == ERROR_MSG
        assert ops.apply is not None

    def test_creation_with_defaults(self, mocked_item_func):
        ops = ItemParser(mocked_item_func)
        assert ops
        assert ops.params is None
        assert not ops.error_msg
        assert ops.apply is not None

"""
Unit tests for item validators and transformers

Classes:
    TestValidatorTransformer

"""
import pytest

from app.cli import ItemTransformer, ItemValidator
from tests.utils import ITEM_OPS_RETURN_VALUE


PARAMS = {'a': 1, 'b': 2}
ERROR_MSG = 'Error'


class TestValidatorTransformer:

    @pytest.fixture(params=[ItemValidator, ItemTransformer])
    def item_ops(self, request):
        return request.param

    def test_creation_with_values(self, item_ops, mocked_item_func):
        ops = item_ops(mocked_item_func, params=PARAMS, error_msg=ERROR_MSG)
        
        assert ops
        assert ops.params == PARAMS
        assert ops.error_msg == ERROR_MSG
        if hasattr(ops, 'validate'):
            assert ops.validate is not None
        else:
                assert ops.transform is not None

    def test_creation_with_defaults(self, item_ops, mocked_item_func):
        ops = item_ops(mocked_item_func)
        assert ops
        assert ops.params is None
        assert not ops.error_msg
        if hasattr(ops, 'validate'):
            assert ops.validate is not None
        else:
                assert ops.transform is not None

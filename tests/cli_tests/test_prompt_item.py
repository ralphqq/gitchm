"""
Tests on prompt items

Classes:
    TestPromptItemGeneric
"""
import pytest

from app.cli import PromptItem
from app.exc import TransformationError, ValidationError


INPUT1 = 'valid-input'
INPUT2 = '42'
INPUT3 = ' '
INPUTS = [INPUT1, INPUT2, INPUT3]
TR_VALUE = 'transformed-value'


class TestPromptItemGeneric:

    @pytest.fixture
    def default_item(self):
        item = PromptItem(
            name='default_item',
            message='Optional field',
        )
        return item

    @pytest.fixture
    def required_item(self):
        item = PromptItem(
            name='required_item',
            message='Required field',
            is_required=True
        )
        return item

    @pytest.fixture
    def mocked_item_methods(self, mocker):
        mocker.patch.object(PromptItem, '_validate', return_value=True)
        mocker.patch.object(PromptItem, '_transform', return_value=TR_VALUE)
    def test_creation_and_defaults(self, default_item, required_item):
        assert default_item.name in repr(default_item)
        assert required_item.name in repr(required_item)

    @pytest.mark.parametrize('input_value', INPUTS)
    def test_process_item_ok(
            self,
            input_value,
            required_item,
            mocked_item_methods
        ):
        required_item.process_input(input_value)
        assert required_item._validate.called_once_with(input_value.strip())
        assert required_item._transform.called_once_with(input_value.strip())
        assert required_item.value == TR_VALUE

    def test_process_item_failed_validation(
            self,
            required_item,
            mocked_item_methods
        ):
            required_item._validate.return_value = False
            required_item.process_input(INPUT1)
            assert not required_item._transform.called
            assert not hasattr(required_item, 'value')

    @pytest.mark.parametrize('input_value', INPUTS)
    def test_validate_required_with_no_validators(
            self,
            input_value,
            required_item
        ):
        if input_value == INPUT3:   # Case when input is empty
            with pytest.raises(ValidationError):
                required_item._validate(input_value.strip())

        else:
            result = required_item._validate(input_value.strip())
            assert result

    def test_validate_empty_input_not_required(self, default_item):
        result = default_item._validate(INPUT3.strip())
        assert result

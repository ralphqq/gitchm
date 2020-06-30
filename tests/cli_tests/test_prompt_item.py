"""
Tests on prompt items

Test Classes:
    TestPromptItemCreationAndProcess
    TestPrompItemValidate
    TestPrompItemTransform
"""
from unittest.mock import call
import pytest

from app.cli import ItemParser, PromptItem
from app.exc import TransformationError, ValidationError


INPUT1 = 'valid-input'
INPUT2 = '42'
INPUT3 = ' '
INPUTS = [INPUT1, INPUT2, INPUT3]
TR_VALUE = 'transformed-value'

VF_SIDE_EFFECT = [True, True, True]
TR_SIDE_EFFECT1 = ['a', 'b', 'c']
TR_SIDE_EFFECT2 = [1, 2, 3]
PARAMS = [{'a': 1, 'b': 2}, {'c': 'some-param'}, None]


class TestPromptItemCreationAndProcess:

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


class TestPrompItemValidate:

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

    def test_validate_with_validators(self, required_item, item_ops_factory):
        validators = item_ops_factory(
            side_effect=VF_SIDE_EFFECT,
            params=PARAMS
        )
        validator_func = validators[0].apply
        required_item.validators = validators
        result = required_item._validate(INPUT1)

        assert result
        assert validator_func.call_count == len(VF_SIDE_EFFECT)
        validator_func.assert_has_calls([
            call(INPUT1, **PARAMS[0]),
            call(INPUT1, **PARAMS[1]),
            call(INPUT1),
        ])

    def test_validate_with_errors(self, required_item, item_ops_factory):
        side_effect = [True, False, True]
        validators = item_ops_factory(
            side_effect=side_effect,
            params=PARAMS
        )
        validator_func = validators[0].apply
        required_item.validators = validators

        with pytest.raises(ValidationError):
            result = required_item._validate(INPUT1)
        assert validator_func.call_count == side_effect.index(False) + 1


class TestPrompItemTransform:

    @pytest.mark.parametrize('input_value', INPUTS)
    def test_transform_required_with_no_transformers(
            self,
            input_value,
            required_item
        ):
        result = required_item._transform(input_value.strip())
        if input_value == INPUT3:   # Case when input is empty
            assert result is None
        else:
            assert result
            assert isinstance(result, required_item.data_type)

    @pytest.mark.parametrize('input_value', INPUTS)
    def test_transformgiven_data_type(self, input_value, required_item):
        required_item.data_type = int
        if input_value == INPUT2:   # value is '42'
            result = required_item._transform(input_value)
            assert result
            assert isinstance(result, required_item.data_type)
        else:
            with pytest.raises(TransformationError):
                required_item._transform(input_value)

    def test_transform_transformers(self, required_item, item_ops_factory):
        transformers = item_ops_factory(
            side_effect=TR_SIDE_EFFECT1,
            params=PARAMS
        )
        transformer_func = transformers[0].apply
        required_item.transformers = transformers
        result = required_item._transform(INPUT1)

        assert result
        assert transformer_func.call_count == len(TR_SIDE_EFFECT1)
        transformer_func.assert_has_calls([
            call(INPUT1, **PARAMS[0]),

            # output of above call is input of below call
            call(TR_SIDE_EFFECT1[0], **PARAMS[1]),

            # output of above call is input of below call
            call(TR_SIDE_EFFECT1[1]),
        ])

    def test_transform_with_errors(self, required_item, item_ops_factory):
        side_effect = ['a', ValueError, 'b']
        transformers = item_ops_factory(
            side_effect=side_effect,
            params=PARAMS
        )
        transformer_func = transformers[0].apply
        required_item.transformers = transformers

        with pytest.raises(TransformationError):
            result = required_item._transform(INPUT1)
        assert transformer_func.call_count == side_effect.index(ValueError) + 1

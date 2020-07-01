"""
Tests for PromptUI code

Fixtures:
    prompt_ui(prompt_items)

Test Classes:
    TestPromptUIStart
    TestPromptUIGetUserInput
    TestPromptUIMiscMethods
"""
from unittest.mock import call, patch

import pytest

from app.cli import PromptItem, PromptUI
from app.exc import TransformationError, ValidationError
from tests.utils import set_attr_or_key


# Constants

NAMES = ['workdir', 'branch', 'author', 'committer']
GROUPS = ['init', 'init', 'reflect', 'reflect']
SIDE_EFFECT = ['/home/usr/repo', 'master', 'Donald', 'Donald']
RETURN_VALUE = 'parsed-value'


# Fixtures

@pytest.fixture
def prompt_ui(prompt_items):
    items = prompt_items(names=NAMES, groups=GROUPS, values=SIDE_EFFECT)
    items[1].depends_on = items[0]
    return PromptUI(prompt_items=items)


# Test Classes

class TestPromptUIStart:

    @pytest.fixture
    def mocked_start_methods(self, mocker):
        mocker.patch.object(
            target=PromptUI,
            attribute='_get_user_input',
            side_effect=SIDE_EFFECT
        )
        mocker.patch.object(
            target=PromptUI,
            attribute='_finalize_options'
        )

    def test_start_ok(self, prompt_ui, mocked_start_methods):
        prompt_ui.start()
        assert prompt_ui._get_user_input.call_count == len(NAMES)
        assert set(prompt_ui.options.keys()) == set(GROUPS)
        prompt_ui._get_user_input.assert_has_calls([
            call(arg) for arg in prompt_ui.prompt_items
        ])
        assert prompt_ui._finalize_options.called

    def test_start_parent_none(self, prompt_ui, mocked_start_methods):
        # Make parent item value None
        new_side_effect = list(SIDE_EFFECT)
        new_side_effect[0] = None
        set_attr_or_key(prompt_ui.prompt_items, 'value', new_side_effect)

        prompt_ui.start()
        actual_calls = prompt_ui._get_user_input.mock_calls

        assert len(actual_calls) == 3
        assert call(prompt_ui.prompt_items[1]) not in actual_calls
        assert prompt_ui._finalize_options.called


class TestPromptUIGetUserInput:

    @pytest.fixture
    def mocked_input_methods(self, mocker):
        mocked_input = mocker.patch('builtins.input', return_value='value')
        mocked_stderr = mocker.patch('app.cli.sys.stderr.write')
        mocker.patch.object(
            target=PromptItem,
            attribute='process_input',
            return_value=RETURN_VALUE
        )
        return mocked_input, mocked_stderr

    def test_input_ok(self, prompt_ui, mocked_input_methods):
        mocked_input ,mocked_stderr = mocked_input_methods

        prompt_item = prompt_ui.prompt_items[0]
        result = prompt_ui._get_user_input(prompt_item)

        assert result == RETURN_VALUE
        mocked_input.assert_called_once()
        prompt_item.process_input.assert_called_once()
        assert not mocked_stderr.called

    def test_input_retries_and_ok(self, prompt_ui, mocked_input_methods):
        mocked_input ,mocked_stderr = mocked_input_methods

        # Fail on first 2 attempts, succeed on 3rd
        side_effect = [ValidationError, TransformationError, RETURN_VALUE]
        num_attempts = len(side_effect)

        prompt_item = prompt_ui.prompt_items[0]
        prompt_item.process_input.side_effect = side_effect
        result = prompt_ui._get_user_input(prompt_item)

        assert result == RETURN_VALUE
        assert mocked_input.call_count == num_attempts
        assert mocked_stderr.call_count == 2
        assert prompt_item.process_input.call_count == num_attempts


class TestPromptUIMiscMethods:

    def test_finalize_options(self, prompt_ui):
        prompt_ui.options['init'] = {'a': None, 'b': 2, 'c': 3}
        prompt_ui.options['reflect'] = {'d': 4, 'e': None, 'f': None}
        prompt_ui._finalize_options()
        assert prompt_ui.options['init'] == {'b': 2, 'c': 3}
        assert prompt_ui.options['reflect'] == {'d': 4}

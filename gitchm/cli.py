"""
CLI

Classes:
    ItemParser
    PromptItem
    PromptUI
"""
from collections import defaultdict
from dataclasses import dataclass
import sys
from typing import Any, Callable, List

from gitchm.exc import TransformationError, ValidationError
from gitchm.utils import clean_dict


# Classes

@dataclass
class ItemParser:
    """Wraps a validator or transformation function."""

    apply: Callable
    params: dict = None
    error_msg: str = ''


@dataclass
class PromptItem:
    """Represents CLI prompt item that user has to fill out."""

    name: str
    message: str
    is_required: bool = False
    data_type: type = str
    active_on: 'PromptItem' = None
    inactive_on: 'PromptItem' = None
    group: str = 'menu'
    validators: List[ItemParser] = None
    transformers: List[ItemParser] = None

    def __repr__(self) -> str:
        return f'<PromptItem {self.name}>'

    def process_input(self, value: str) -> None:
        """Applies validators and transformers to raw value of input."""
        value = value.strip()
        if self._validate(value):
            self.value = self._transform(value)
            return self.value

    def _validate(self, value: str) -> bool:
        """Checks if value meets validation rules.

        This method returns `True` only when value 
        passes all validation rules; otherwise, 
        it raises `ValidationError`.
        """
        if not value and self.is_required:
            raise ValidationError(f'This is a required field.')

        if self.validators is not None:
            for v in self.validators:
                params = v.params or {}
                result = v.apply(value, **params)

                if not result:
                    raise ValidationError(
                        f'Error validating {self.name}: {v.error_msg}'
                    )

        return True

    def _transform(self, value: str) -> Any:
        """Casts value into given data type and applies transformations."""
        if not value:
            return None

        try:
            val = self.data_type(value)

            if self.transformers is not None:
                for t in self.transformers:
                    params = t.params or {}
                    val = t.apply(val, **params)

            return val

        except Exception as e:
            raise TransformationError(f'Error during transformation {e}')


class PromptUI:

    def __init__(self, prompt_items: List[PromptItem]) -> None:
        self.prompt_items = prompt_items
        self.options = defaultdict(dict)

    def start(self) -> None:
        for prompt_item in self.prompt_items:
            if self._skip_item(prompt_item):
                continue

            value = self._get_user_input(prompt_item)
            if value is not None:
                group = prompt_item.group
                name = prompt_item.name
                self.options[group][name] = value

        self._finalize_options()

    def _get_user_input(self, prompt_item: PromptItem) -> Any:
        while True:
            try:
                value = input(prompt_item.message)
                return prompt_item.process_input(value)

            except (TransformationError, ValidationError) as e:
                sys.stderr.write(f'{e}')

            except KeyboardInterrupt:
                break

    def _skip_item(self, prompt_item: PromptItem) -> bool:
        """Checks if prompt_item should be skipped or not."""
        activator = prompt_item.active_on
        inactivator = prompt_item.inactive_on
        return bool(
            (activator and getattr(activator, 'value', None) is None) or
            (inactivator and getattr(inactivator, 'value', None) is not None)
        )

    def _finalize_options(self) -> None:
        self.options = {
            group: clean_dict(values) for group, values in self.options.items()
        }

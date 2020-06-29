"""
CLI

Classes:
    ItemValidator
    ItemTransformer
    PromptItem
    PromptUI
"""
from dataclasses import dataclass
from typing import Any, Callable, List

from app.exc import TransformationError, ValidationError


# Classes

@dataclass
class ItemValidator:
    validate: Callable
    params: dict = None
    error_msg: str = ''


@dataclass
class ItemTransformer:
    transform: Callable
    params: dict = None
    error_msg: str = ''


@dataclass
class PromptItem:
    """Represents CLI prompt item that user has to fill out."""

    name: str
    message: str
    is_required: bool = False
    data_type: type = str
    depends_on: 'PromptItem' = None
    validators: List[ItemValidator] = None
    transformers: List[ItemTransformer] = None

    def __repr__(self) -> str:
        return f'<PromptItem {self.name}>'

    def process_input(self, value: str) -> None:
        """Applies validators and transformers to raw value of input."""
        value = value.strip()
        if self._validate(value):
            self.value = self._transform(value)

    def _validate(self, value: str) -> bool:
        if not value and self.is_required:
            raise ValidationError(f'This is a required field.')
        for v in self.validators:
                result = v.validate(value, **v.params)
                if not result:
                    raise ValidationError(
                        f'Error validating {self.name}: {v.error_msg}'
                    )

    def _transform(self, value: str) -> Any:
        try:
            val = self.data_type(value)
            for t in self.transformers:
                val = t.transform(val, **t.params)

            return val

        except Exception as e:
            raise TransformationError(f'Error during transformation {e}')


class PromptUI:
    pass

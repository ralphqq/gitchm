"""
CLI

Classes:
    ItemValidator
    ItemTransformer
    ItemParser
    PromptItem
    PromptUI
"""
from dataclasses import dataclass
from typing import Any, Callable, List

from app.exc import TransformationError, ValidationError


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
    depends_on: 'PromptItem' = None
    validators: List[ItemParser] = None
    transformers: List[ItemParser] = None

    def __repr__(self) -> str:
        return f'<PromptItem {self.name}>'

    def process_input(self, value: str) -> None:
        """Applies validators and transformers to raw value of input."""
        value = value.strip()
        if self._validate(value):
            self.value = self._transform(value)

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
                result = v.validate(value, **v.params)

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
                    val = t.transform(val, **t.params)

            return val

        except Exception as e:
            raise TransformationError(f'Error during transformation {e}')


class PromptUI:
    pass

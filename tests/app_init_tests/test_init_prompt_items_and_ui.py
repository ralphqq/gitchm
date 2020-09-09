import pytest

from gitchm.init import INIT, PROMPT_ITEMS, REFLECT, ui
from gitchm.cli import PromptItem, PromptUI


class TestInitPromptItemsAndUI:
    @pytest.mark.parametrize("item", PROMPT_ITEMS)
    def test_prompt_items(self, item):
        assert isinstance(item, PromptItem)
        assert repr(item) is not None
        assert item.message is not None
        assert item.group in [INIT, REFLECT]

    def test_prompt_ui(self):
        assert isinstance(ui, PromptUI)
        assert PROMPT_ITEMS == ui.prompt_items

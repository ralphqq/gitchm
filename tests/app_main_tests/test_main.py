import logging
from unittest.mock import MagicMock

import pytest

from gitchm.init import INIT, REFLECT
from gitchm.main import main

DEST_WORKDIR = "some/workdir/path"
OPTIONS = {INIT: {"source_workdir": "/tmp"}, REFLECT: {"author": "name"}}


class TestMainEntryPoint:
    @pytest.fixture
    def mocked_main_funcs(self, mocker):
        # Mock the PromptUI instance
        mocked_ui = mocker.patch("gitchm.main.ui")
        mocked_ui.options = OPTIONS

        # Mock the CommitHistoryMirror object
        mocked_chm_constructor = mocker.patch(
            "gitchm.main.CommitHistoryMirror"
        )
        mocked_chm = mocked_chm_constructor.return_value
        mocked_chm.reflect = MagicMock()  # AsyncMock throws warning

        mocker.patch("gitchm.main.asyncio.run")
        return mocked_ui, mocked_chm_constructor, mocked_chm

    @pytest.mark.parametrize(
        "stats",
        [
            {"replicated": 3, "skipped": 0, "failed": 1},
            {"replicated": 0},
        ],
    )
    def test_main_results(self, stats, mocked_main_funcs, caplog):
        caplog.set_level(logging.INFO)
        mocked_ui, mocked_chm_constructor, mocked_chm = mocked_main_funcs
        mocked_chm.stats = stats
        main()

        assert mocked_ui.start.called
        assert mocked_chm_constructor.called_once_with(**OPTIONS[INIT])
        assert mocked_chm.reflect.called_once_with(**OPTIONS[REFLECT])

        for record in caplog.records:
            assert record.levelname != "ERROR"

        if len(stats) == 3:
            assert "To view replicated" in caplog.text
        else:
            assert "To view replicated" not in caplog.text

    @pytest.mark.parametrize(
        "error,text",
        [
            (KeyboardInterrupt, "Canceled"),
            (ValueError, "An unhandled error occurred"),
        ],
    )
    def test_main_exceptions(self, error, text, mocked_main_funcs, caplog):
        caplog.set_level(logging.INFO)
        mocked_ui, mocked_chm_constructor, mocked_chm = mocked_main_funcs
        mocked_ui.start.side_effect = error
        main()
        assert text in caplog.text

import os
import re
import shutil

import pytest

from app.utils import clean_dict, create_dir, delete_dir


DUMMY_DIR = 'dummy-dir'


class TestCreateDirectories:

    @pytest.fixture
    def mock_dir_ops(self, mocker):
        mocker.patch('os.makedirs')
        mocker.patch('shutil.rmtree')

    @pytest.fixture
    def init_dummy_dir(self, init_chm_test_session):
        dummy_dir = os.path.join(
            init_chm_test_session,
            DUMMY_DIR
        )
        if not os.path.exists(dummy_dir):
            os.makedirs(dummy_dir)
        yield dummy_dir, init_chm_test_session
        delete_dir(dummy_dir)

    def test_create_new_dir(self, init_chm_test_session, mock_dir_ops):
        new_path = os.path.join(
            init_chm_test_session,
            'a-very-new-directory'
        )
        result_dir = create_dir(new_path)
        assert result_dir == new_path
        assert os.makedirs.called_once_with(new_path)
        assert not shutil.rmtree.called

    def test_create_raise_on_conflict(self, init_dummy_dir, mock_dir_ops):
        existing_path, _ = init_dummy_dir
        with pytest.raises(ValueError):
            result_dir = create_dir(existing_path)
        assert not os.makedirs.called
        assert not shutil.rmtree.called

    def test_create_replace_on_conflict(self, init_dummy_dir, mock_dir_ops):
        existing_path, _ = init_dummy_dir
        result_dir = create_dir(existing_path, on_conflict='replace')
        assert result_dir == existing_path
        assert os.makedirs.called_once_with(existing_path)
        assert shutil.rmtree.called_once_with(existing_path)

    def test_create_resolve_on_conflict(self, init_dummy_dir, mock_dir_ops):
        existing_path, _ = init_dummy_dir
        result_dir = create_dir(existing_path, on_conflict='resolve')
        assert result_dir != existing_path
        assert os.makedirs.called_once_with(result_dir)
        assert re.search(fr'{existing_path}-\d{{14}}', result_dir) is not None
        assert not shutil.rmtree.called


class TestMiscUtils:

    def test_dict_cleanup(self):
        orig_dict = {'a': 1, 'b': None, 'c': '', 'd': 0}
        new_dict = clean_dict(orig_dict)
        assert 'a' in new_dict
        assert 'b' not in new_dict
        assert 'c' in new_dict
        assert 'd' in new_dict

"""
End-to-end mirror ops test under different scenarios

Classes:
    TestMirrorAutoDestRepo

"""
import os

from git import Repo
import pytest

from app.mirror import CommitHistoryMirror
from app.utils import delete_dir
from tests.utils import (
    listify_attribute,
    load_iter_commits,
    read_gitchm
)


class TestMirrorAutoDestRepo:
    """Case where destination repo is not specified."""

    @pytest.fixture
    async def m(self, init_mirror):
        mirror = await init_mirror()
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)

    @pytest.mark.asyncio
    async def test_has_correct_commits(self, m):
        src_commits = load_iter_commits(m.source_repo, mode='obj')
        src_messages = listify_attribute(src_commits, 'message')
        dst_commits = load_iter_commits(m.dest_repo, mode='obj')
        dst_messages = listify_attribute(dst_commits, 'message')
        assert set(src_messages) == set(dst_messages)

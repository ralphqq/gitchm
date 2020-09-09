"""
End-to-end mirror ops tests for different scenarios
involving non-mirror destination repos.

Test Classes:
    TestMirrorOpsAutoDestRepo
    TestMirrorOpsEmptyDestRepo
    TestMirrorOpsNoTreeDestRepo
    TestMirrorOpsWithTreeDestRepo
"""
import os

from git import Repo
import pytest

from gitchm.utils import delete_dir
from tests.utils import listify_attribute, load_iter_commits, read_gitchm


class TestMirrorOpsAutoDestRepo:
    """Case where destination repo is not specified.

    This class will also be inherited by other test classes in this
    module.
    """

    @pytest.fixture
    async def m(self, init_mirror):
        mirror = await init_mirror()
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)

    @pytest.mark.asyncio
    async def test_has_correct_commits(self, m):
        src_commits = load_iter_commits(m.source_repo, mode="obj")
        src_messages = listify_attribute(src_commits, "message")
        src_hashes = listify_attribute(src_commits, "hexsha")
        dst_commits = load_iter_commits(m.dest_repo, mode="obj")
        dst_messages = listify_attribute(dst_commits, "message")
        dst_replicated_hashes = read_gitchm(m.dest_repo.working_dir)

        assert set(src_messages).issubset(set(dst_messages))
        assert set(src_hashes) == set(dst_replicated_hashes)


class TestMirrorOpsEmptyDestRepo(TestMirrorOpsAutoDestRepo):
    """Destination is given but is an empty directory."""

    @pytest.fixture
    async def m(self, init_mirror, non_git_repo):
        mirror = await init_mirror(dest_workdir=non_git_repo)
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)


class TestMirrorOpsNoTreeDestRepo(TestMirrorOpsAutoDestRepo):
    """Destination is given but has no working tree head."""

    @pytest.fixture
    async def m(self, init_mirror, dest_repo_no_tree):
        mirror = await init_mirror(dest_workdir=dest_repo_no_tree.working_dir)
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)


class TestMirrorOpsWithTreeDestRepo(TestMirrorOpsAutoDestRepo):
    """Destination repo has working tree but is a non-mirror repo."""

    @pytest.fixture
    async def m(self, init_mirror, dest_repo_tree):
        mirror = await init_mirror(dest_workdir=dest_repo_tree.working_dir)
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)

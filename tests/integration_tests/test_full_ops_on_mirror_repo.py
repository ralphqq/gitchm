"""
End-to-end mirror ops tests for different scenarios 
involving mirror destination repos.

Test Classes:
    TestMirrorOpsDestMaster
"""
import pytest

from app.utils import delete_dir
from tests.utils import (
    DEST_FEATURE_COMMITS,
    DEST_MASTER_COMMITS,
    FEATURE_BRANCH,
    listify_attribute,
    load_iter_commits,
    read_gitchm
)


class TestMirrorOpsDestMaster:
    """Mirror ops on destination repo's master branch."""

    @pytest.fixture
    async def m(self, init_mirror, dest_repo_mirror_master):
        mirror = await init_mirror(
            dest_workdir=dest_repo_mirror_master.working_dir
        )
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)

    @pytest.mark.asyncio
    async def test_ops_correct_results(self, m):
        # Get number of replicated commits
        total_commits_dest = len(load_iter_commits(m.dest_repo))
        new_commits_dest = total_commits_dest - DEST_MASTER_COMMITS

        # Get list of commit hashes from source and .gitchmirror
        src_commits = load_iter_commits(m.source_repo, mode='obj')
        src_hashes = listify_attribute(src_commits, 'hexsha')
        dst_replicated_hashes = read_gitchm(m.dest_repo.working_dir)

        assert m.stats['replicated'] == new_commits_dest
        assert m.stats['skipped'] == DEST_MASTER_COMMITS
        assert m.stats['failed'] == 0
        assert set(src_hashes) == set(dst_replicated_hashes)
        assert m.dest_repo.head.ref == m.dest_repo.heads.master


class TestMirrorOpsDestFeature:
    """Mirror ops on destination repo's feature branch."""

    @pytest.fixture
    async def m(self, init_mirror, dest_repo_mirror_feature):
        mirror = await init_mirror(
            dest_workdir=dest_repo_mirror_feature.working_dir,
            dest_branch=FEATURE_BRANCH
        )
        yield mirror
        delete_dir(mirror.dest_repo.working_dir)

    @pytest.mark.asyncio
    async def test_ops_correct_results(self, m):
        # Get number of replicated commits
        total_commits_dest = len(load_iter_commits(m.dest_repo, branch=FEATURE_BRANCH))
        new_commits_dest = total_commits_dest - DEST_FEATURE_COMMITS

        # Get list of commit hashes from source and .gitchmirror
        src_commits = load_iter_commits(m.source_repo, mode='obj')
        src_hashes = listify_attribute(src_commits, 'hexsha')
        dst_replicated_hashes = read_gitchm(m.dest_repo.working_dir)

        assert m.stats['replicated'] == new_commits_dest
        assert m.stats['skipped'] == DEST_FEATURE_COMMITS
        assert m.stats['failed'] == 0
        assert set(src_hashes) == set(dst_replicated_hashes)
        assert m.dest_repo.head.ref == m.dest_repo.active_branch

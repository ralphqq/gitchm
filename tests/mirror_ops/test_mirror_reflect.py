from unittest.mock import AsyncMock, patch

from git import Repo
from git.exc import GitError
import pytest

from app.mirror import CommitHistoryMirror
from tests.utils import FEATURE_BRANCH


class TestMirrorOpsReflect:

    @pytest.fixture
    def mocked_methods(self, mocker, iter_commits):
        """Monkey-patches all CHM methods called in reflect."""
        mocker.patch.object(
            target=CommitHistoryMirror,
            attribute='_set_active_dest_branch'
        )
        mocker.patch.object(
            target=Repo,
            attribute='iter_commits',
            side_effect=iter_commits
        )
        mocker.patch.object(
            target=CommitHistoryMirror,
            attribute='_replicate',
            new_callable=AsyncMock
        )

    @pytest.fixture
    def mirror_new_dest(self, chm, mocked_methods):
        """CHM with new repo as dest."""
        return chm['mirror']

    @pytest.fixture
    def mirror_old_dest(self, chm_dest_master, mocked_methods):
        """CHM with newold as dest."""
        return chm_dest_master['mirror']

    @pytest.mark.asyncio
    async def test_reflect_no_args_to_new_dest(self, mirror_new_dest):
        branch = 'master'
        params = {'rev': branch, 'regexp_ignore_case': True}
        m = mirror_new_dest
        await m.reflect()
        assert not m._set_active_dest_branch.called
        assert Repo.iter_commits.call_args.kwargs == params
        assert m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_no_args_to_old_dest(self, mirror_old_dest):
        branch = 'master'
        params = {'rev': branch, 'regexp_ignore_case': True}
        m = mirror_old_dest
        await m.reflect()
        assert m._set_active_dest_branch.called_once_with(branch)
        assert Repo.iter_commits.call_args.kwargs == params
        assert m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_to_branch_in_new_dest(self, mirror_new_dest):
        source_branch = 'master'
        dest_branch = 'feature-branch'
        params = {'rev': source_branch, 'regexp_ignore_case': True}
        m = mirror_new_dest

        with pytest.raises(ValueError):
            await m.reflect(dest_branch=dest_branch)

        assert not m._set_active_dest_branch.called
        assert not Repo.iter_commits.called
        assert not m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_valid_args_to_new_dest(self, mirror_new_dest):
        author = 'author'
        committer = 'committer'
        before = '2020-06-01'
        after = '2020-05-15'
        source_branch = 'other-branch'

        params = {
            'rev': source_branch,
            'author': author,
            'committer': committer,
            'before': before,
            'after': after,
            'regexp_ignore_case': True,
        }
        m = mirror_new_dest
        await m.reflect(
            author=author,
            committer=committer,
            before=before,
            after=after,
            source_branch=source_branch
        )
        assert not m._set_active_dest_branch.called
        assert Repo.iter_commits.call_args.kwargs == params
        assert m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_valid_args_to_old_dest(self, mirror_old_dest):
        author = 'author'
        committer = 'committer'
        before = '2020-06-01'
        after = '2020-05-15'
        source_branch = 'other-branch'
        dest_branch = FEATURE_BRANCH

        params = {
            'rev': source_branch,
            'author': author,
            'committer': committer,
            'before': before,
            'after': after,
            'regexp_ignore_case': True,
        }
        m = mirror_old_dest
        await m.reflect(
            author=author,
            committer=committer,
            before=before,
            after=after,
            source_branch=source_branch,
            dest_branch=dest_branch
        )
        assert m._set_active_dest_branch.called_once_with(dest_branch)
        assert Repo.iter_commits.call_args.kwargs == params
        assert m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_error_to_new_dest(self, mirror_new_dest):
        Repo.iter_commits.side_effect = GitError
        m = mirror_new_dest
        with patch('app.mirror.logger.error') as mock_log_error:
            await m.reflect()
            assert mock_log_error.called

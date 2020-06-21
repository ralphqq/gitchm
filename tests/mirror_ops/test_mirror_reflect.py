from unittest.mock import AsyncMock, patch

from git import Repo
from git.exc import GitError
import pytest

from app.mirror import CommitHistoryMirror


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

    @pytest.mark.asyncio
    async def test_reflect_no_args(self, chm, mocked_methods):
        branch = 'master'
        params = {'rev': branch, 'regexp_ignore_case': True}
        m = chm['mirror']
        await m.reflect()
        assert m._set_active_dest_branch.called_once_with(branch)
        assert Repo.iter_commits.call_args.kwargs == params
        assert m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_dest_branch(self, chm, mocked_methods):
        source_branch = 'master'
        dest_branch = 'feature-branch'
        params = {'rev': source_branch, 'regexp_ignore_case': True}
        m = chm['mirror']
        await m.reflect(dest_branch=dest_branch)
        assert m._set_active_dest_branch.called_once_with(dest_branch)
        assert Repo.iter_commits.call_args.kwargs == params
        assert m._replicate.called

    @pytest.mark.asyncio
    async def test_reflect_with_args(self, chm, mocked_methods):
        author = 'author'
        committer = 'committer'
        before = '2020-06-01'
        after = '2020-05-15'
        source_branch = 'other-branch'
        dest_branch = 'feature-branch'

        params = {
            'rev': source_branch,
            'author': author,
            'committer': committer,
            'before': before,
            'after': after,
            'regexp_ignore_case': True,
        }
        m = chm['mirror']
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
    async def test_reflect_with_error(self, chm, mocked_methods):
        Repo.iter_commits.side_effect = GitError
        m = chm['mirror']
        with patch('app.mirror.logger.error') as mock_log_error:
            await m.reflect()
            assert mock_log_error.called

from git import IndexFile
from git.exc import GitError
import pytest

from gitchm.mirror import CommitHistoryMirror
from tests.utils import FEATURE_BRANCH, load_iter_commits


class TestCommit:

    @pytest.fixture
    def mocked_stuff(self, mocker):
        mocker.patch.object(CommitHistoryMirror, '_replicate')
        mocker.patch.object(IndexFile, 'add')
        mocker.patch.object(IndexFile, 'commit')

    async def setup_mirror(self, chm_dict, commit_num=None, **kwargs):
        """Initializes mirror and loads commit object to replicate.

        Args:
            chm_obj (dict): The dictionary returned by a chm fixture
            commit_num (int): The list index of the commit to return
            kwargs: Keyword args of the method `reflect()` method

        Returns:
            tuple: mirror, commit
        """
        c = None
        m = chm_dict['mirror']
        await m.reflect(**kwargs)
        if commit_num is not None:
            commits = load_iter_commits(m.source_repo, mode='obj')
            c = commits[commit_num]
        return m, c

    @pytest.mark.asyncio
    async def test_mirror_commit_skipped(self, chm_dest_master, mocked_stuff):
        m, _ = await self.setup_mirror(chm_dest_master)

        # Try to mirror a commit already in dest repo
        mirrored_commit = m.source_repo.head.commit
        result = await m._commit(0, mirrored_commit)

        assert result == 'skipped'
        assert not IndexFile.add.called
        assert not IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_error_result(self, chm, mocked_stuff):
        num = 0
        m, c = await self.setup_mirror(chm, num)

        # Throw an error
        IndexFile.add.side_effect = GitError
        result = await m._commit(num, c)
        assert result == 'failed'

    @pytest.mark.asyncio
    async def test_commit_no_tree(self, chm, mocked_stuff):
        num = 0
        m, c = await self.setup_mirror(chm, num)

        result = await m._commit(num, c)

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_with_tree(self, chm_dest_tree, mocked_stuff):
        num = 0
        m, c = await self.setup_mirror(chm_dest_tree, num)

        result = await m._commit(num, c)

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_dest_master(self, chm_dest_master, mocked_stuff):
        num = -1
        m, c = await self.setup_mirror(chm_dest_master, num)

        result = await m._commit(num, c)

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_dest_feature(self, chm_dest_feature, mocked_stuff):
        num = -1
        m, c = await self.setup_mirror(
            chm_dict=chm_dest_feature,
            commit_num=num,
            dest_branch=FEATURE_BRANCH
        )

        result = await m._commit(num, c)

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

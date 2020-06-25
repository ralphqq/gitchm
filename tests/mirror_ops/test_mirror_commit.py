from git import IndexFile
from git.exc import GitError
import pytest

from app.mirror import CommitHistoryMirror
from tests.utils import load_iter_commits


class TestCommit:

    @pytest.fixture
    def mocked_stuff(self, mocker):
        mocker.patch.object(CommitHistoryMirror, '_replicate')
        mocker.patch.object(IndexFile, 'add')
        mocker.patch.object(IndexFile, 'commit')

    async def setup_mirror(self, chm_object, **kwargs):
        m = chm_object['mirror']
        await m.reflect(**kwargs)
        return m

    @pytest.mark.asyncio
    async def test_mirror_commit_skipped(self, chm_dest_master, mocked_stuff):
        m = await self.setup_mirror(chm_dest_master)

        # Try to mirror a commit already in dest repo
        mirrored_commit = m.source_repo.head.commit
        result = await m._commit(0, mirrored_commit)

        assert result == 'skipped'
        assert not IndexFile.add.called
        assert not IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_error_result(self, chm, mocked_stuff):
        m = await self.setup_mirror(chm)

        # Load a source commit not yet in dest
        commits = load_iter_commits(m.source_repo, mode='obj')
        
        # Throw an error
        IndexFile.add.side_effect = GitError
        result = await m._commit(0, commits[0])
        assert result == 'failed'

    @pytest.mark.asyncio
    async def test_commit_no_tree(self, chm, mocked_stuff):
        m = await self.setup_mirror(chm)

        # Load a source commit not yet in dest
        commits = load_iter_commits(m.source_repo, mode='obj')
        result = await m._commit(0, commits[0])

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_with_tree(self, chm_dest_tree, mocked_stuff):
        m = await self.setup_mirror(chm_dest_tree)

        # Load a source commit not yet in dest
        commits = load_iter_commits(m.source_repo, mode='obj')
        result = await m._commit(0, commits[0])

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_dest_master(self, chm_dest_master, mocked_stuff):
        m = await self.setup_mirror(chm_dest_master)

        # Load a source commit not yet in dest
        commits = load_iter_commits(m.source_repo, mode='obj')
        result = await m._commit(0, commits[-1])

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

    @pytest.mark.asyncio
    async def test_commit_dest_feature(self, chm_dest_feature, mocked_stuff):
        m = await self.setup_mirror(chm_dest_feature)

        # Load a source commit not yet in dest
        commits = load_iter_commits(m.source_repo, mode='obj')
        result = await m._commit(0, commits[-1])

        assert result == 'replicated'
        assert IndexFile.add.called
        assert IndexFile.commit.called

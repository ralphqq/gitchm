import os
import tempfile

from git import Repo
import pytest

from app.mirror import CommitHistoryMirror


class TestSourceRepoAccess:

    @pytest.fixture
    def mock_init_repos(self, mocker):
        """Mocks the repo _init methods called in constructor."""
        mocker.patch.object(CommitHistoryMirror, '_init_source_repo')

    @pytest.fixture
    def modified_chm(self, init_source_repo):
        """Modifies CommitHistoryMirror class."""
        source_workdir, parent_dir_path, commit_data = init_source_repo

        class ModifiedCHM(CommitHistoryMirror):
            """Overrides parent class's __init__ method.

            This makes it possible to separately test each 
            method called in the original class's __init__ method.
            """

            def __init__(self):
                self.source_workdir = source_workdir

        return {
            'mirror': ModifiedCHM(),
            'source_workdir': source_workdir,
            'parent_dir': parent_dir_path,
            'commits': commit_data,
        }

    @pytest.fixture(scope='class')
    def chm(self, init_source_repo):
        """Initializes CommitHistoryMirror session."""
        source_repo_path, parent_dir_path, commit_data = init_source_repo
        mirror = CommitHistoryMirror(source_repo_path)
        return {
            'mirror': mirror,
            'source_workdir': source_repo_path,
            'parent_dir': parent_dir_path,
            'commits': commit_data,
        }

    def test_mirror_initialization(self, mock_init_repos):
        some_dir = '/tmp/foo/bar'
        mirror = CommitHistoryMirror(some_dir)

        assert mirror.source_workdir == some_dir
        assert mirror._init_source_repo.called

    def test_source_repo_init(self, modified_chm):
        mirror = modified_chm['mirror']
        mirror._init_source_repo()
        all_commits = list(mirror.source_repo.iter_commits('master'))
        source_repo_name = os.path.split(modified_chm['source_workdir'])[-1]

        assert len(all_commits) == len(modified_chm['commits'])
        assert mirror.source_workdir == modified_chm['source_workdir']
        assert mirror.source_repo_name == source_repo_name
        assert mirror.parent_dir == modified_chm['parent_dir']

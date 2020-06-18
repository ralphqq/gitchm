import os
import tempfile
from unittest.mock import patch

from git import Repo
from git.exc import GitCommandError, GitError
import pytest

from app.mirror import CommitHistoryMirror
from app.utils import create_dir, delete_dir
from tests.utils import DEST_REPO_PREFIX, ModifiedCHM


class TestMirrorOverallInit:

    @pytest.fixture
    def mock_init_repos(self, mocker):
        """Mocks the repo _init methods called in constructor."""
        mocker.patch.object(CommitHistoryMirror, '_init_source_repo')
        mocker.patch.object(CommitHistoryMirror, '_init_empty_dest_repo')
        mocker.patch.object(CommitHistoryMirror, '_init_existing_dest_repo')

    def test_mirror_init_with_no_dest_workdir(self, mock_init_repos):
        some_dir = '/tmp/foo/bar'
        mirror = CommitHistoryMirror(some_dir)

        assert mirror.source_workdir == some_dir
        assert mirror._init_source_repo.called
        assert mirror._init_empty_dest_repo.called
        assert not mirror._init_existing_dest_repo.called
        assert not mirror.dest_exists
        assert mirror.dest_prefix == 'mirror'

    def test_mirror_init_with_dest_workdir(self, mock_init_repos):
        some_dir = '/tmp/foo/bar'
        some_other_dir = '/tmp/spam/eggs'
        mirror = CommitHistoryMirror(some_dir, some_other_dir)

        assert mirror.source_workdir == some_dir
        assert mirror._init_source_repo.called
        assert not mirror._init_empty_dest_repo.called
        assert mirror._init_existing_dest_repo.called_once_with(some_other_dir)
        assert mirror.dest_exists

    def test_mirror_init_with_same_dest_workdir(self, mock_init_repos):
        some_dir = '/tmp/foo/bar'
        with pytest.raises(ValueError):
            mirror = CommitHistoryMirror(some_dir, some_dir)

    def test_mirror_init_with_dest_prefix(self, mock_init_repos):
        some_dir = '/tmp/foo/bar'
        dest_prefix = 'another-prefix'
        mirror = CommitHistoryMirror(some_dir, prefix=dest_prefix)
        assert mirror.dest_prefix == dest_prefix


class TestSourceAndDestinationRepoInit:

    @pytest.fixture
    def modified_chm(self, init_source_repo):
        """Creates an instance of a ModifiedCHM object."""
        source_workdir, parent_dir_path, commit_data = init_source_repo
        mirror = ModifiedCHM(source_workdir)
        return {
            'mirror': mirror,
            'source_workdir': source_workdir,
            'parent_dir': parent_dir_path,
            'commits': commit_data,
        }

    @pytest.fixture
    def non_git_repo(self, init_source_repo):
        """Sets up and tears down a directory that is not a git repo."""
        _, parent_dir, _ = init_source_repo

        # Create
        non_git_dir_path = create_dir(
            full_path=os.path.join(
                tempfile.gettempdir(),
                'non-git-repo'
            ),
            on_conflict='replace'
        )

        yield non_git_dir_path

        # Delete the non-git repo
        delete_dir(non_git_dir_path)

    def test_source_repo_init(self, modified_chm):
        mirror = modified_chm['mirror']
        mirror._init_source_repo()
        all_commits = list(mirror.source_repo.iter_commits('master'))
        source_repo_name = os.path.split(modified_chm['source_workdir'])[-1]

        assert len(all_commits) == len(modified_chm['commits'])
        assert mirror.source_workdir == modified_chm['source_workdir']
        assert mirror.source_repo_name == source_repo_name
        assert mirror.parent_dir == modified_chm['parent_dir']

    def test_source_repo_init_on_non_git(self, modified_chm, non_git_repo):
        mirror = modified_chm['mirror']
        mirror.source_workdir = non_git_repo
        with pytest.raises(GitError):
            mirror._init_source_repo()

    def test_empty_dest_repo_init(self, modified_chm):
        mirror = modified_chm['mirror']
        mirror._init_source_repo()
        mirror._init_empty_dest_repo()

        source_repo_name = os.path.split(modified_chm['source_workdir'])[-1]
        dest_parent_dir = os.path.split(mirror.dest_workdir)[0]

        assert Repo(mirror.dest_workdir)
        assert isinstance(mirror.dest_repo, Repo)
        assert dest_parent_dir == modified_chm['parent_dir']
        assert mirror.dest_repo_name == f'{DEST_REPO_PREFIX}-{source_repo_name}'
        with pytest.raises(GitCommandError):
            # Raises error because repo has no commits yet
            list(mirror.dest_repo.iter_commits('master'))

    def test_existing_non_git_dest_repo_init(self, modified_chm, non_git_repo):
        mirror = modified_chm['mirror']
        mirror._init_source_repo()

        with patch.object(Repo, 'init') as mock_repo_init:
            mirror._init_existing_dest_repo(non_git_repo)
            assert mock_repo_init.called_once_with(non_git_repo)
        assert mirror.dest_workdir == non_git_repo

    def test_existing_git_dest_repo_init(self, modified_chm, non_git_repo):
        mirror = modified_chm['mirror']
        mirror._init_source_repo()

        # Convert the non-git dir into a git repo
        # before calling the dest initialization method
        Repo.init(non_git_repo)

        with patch.object(Repo, 'init') as mock_repo_init:
            mirror._init_existing_dest_repo(non_git_repo)
            assert not mock_repo_init.called
        assert mirror.dest_workdir == non_git_repo

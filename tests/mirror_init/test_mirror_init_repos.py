import os
import tempfile
from unittest.mock import patch

from git import Repo
from git.exc import GitCommandError, GitError
import pytest

from app.utils import create_dir, delete_dir
from tests.utils import DEST_REPO_PREFIX, ModifiedCHM


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
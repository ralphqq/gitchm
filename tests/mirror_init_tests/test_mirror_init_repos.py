import os
import tempfile
from unittest.mock import patch

from git import Repo
from git.exc import GitCommandError, GitError
import pytest

from app.mirror import CommitHistoryMirror
from app.utils import create_dir, delete_dir
from tests.utils import DEST_REPO_PREFIX, ModifiedCHM


class TestSourceAndDestinationRepoInit:

    @pytest.fixture
    def mocked_calls(self, mocker):
        mocker.patch.object(Repo, 'init')
        mocker.patch.object(CommitHistoryMirror, '_check_tree_state')

    def test_source_repo_init(self, modified_chm):
        mirror = modified_chm['mirror']
        all_commits = list(mirror.source_repo.iter_commits('master'))
        source_repo_name = os.path.split(modified_chm['source_workdir'])[-1]

        assert len(all_commits) == len(modified_chm['commits'])
        assert mirror.source_workdir == modified_chm['source_workdir']
        assert mirror.source_repo_name == source_repo_name
        assert mirror.parent_dir == modified_chm['parent_dir']

    def test_source_repo_init_on_non_git(self, non_git_repo):
        mirror = ModifiedCHM(non_git_repo)
        with pytest.raises(GitError):
            mirror._init_source_repo()

    def test_empty_dest_repo_init(self, modified_chm):
        mirror = modified_chm['mirror']
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

    def test_existing_non_git_dest_repo_init(
            self,
            modified_chm,
            non_git_repo,
            mocked_calls
        ):
        mirror = modified_chm['mirror']
        mirror._init_existing_dest_repo(non_git_repo)

        assert Repo.init.called_once_with(non_git_repo)
        assert not mirror._check_tree_state.called
        assert mirror.dest_workdir == non_git_repo
        assert not mirror.prior_dest_exists

    def test_existing_git_dest_repo_no_tree_init(
            self,
            modified_chm,
            dest_repo_no_tree,
            mocked_calls
        ):
        working_dir = dest_repo_no_tree.working_dir
        mirror = modified_chm['mirror']
        mirror._init_existing_dest_repo(working_dir)

        assert not Repo.init.called
        assert mirror._check_tree_state.called
        assert mirror.dest_workdir == working_dir
        assert mirror.prior_dest_exists

    def test_existing_git_dest_repo_init(
            self,
            modified_chm,
            dest_repo_tree,
            mocked_calls
        ):
        working_dir = dest_repo_tree.working_dir
        mirror = modified_chm['mirror']
        mirror._init_existing_dest_repo(working_dir)

        assert not Repo.init.called
        assert mirror._check_tree_state.called
        assert mirror.dest_workdir == working_dir
        assert mirror.prior_dest_exists

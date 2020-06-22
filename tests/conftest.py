"""
Fixtures used throughout the test suite

Fixtures:
    init_chm_test_session()
    init_source_repo(init_chm_test_session)
    non_git_repo(init_source_repo)
"""
import os
import tempfile

from git import Repo
import pytest

from app.utils import create_dir, delete_dir
from tests.utils import make_commits


PARENT_DIR = 'chm-test-session'
SOURCE_WORKDIR = 'project-src'


@pytest.fixture(scope='session')
def init_chm_test_session():
    """Creates and removes the main directory for the test session."""
    tmp_dir = tempfile.gettempdir()
    
    # Create the main directory
    parent_dir_path = create_dir(
        full_path=os.path.join(tmp_dir, PARENT_DIR),
        on_conflict='replace'
    )
    yield parent_dir_path

    # Delete the entire main directory
    delete_dir(parent_dir_path)


@pytest.fixture(scope='module')
def init_source_repo(init_chm_test_session):
    """Sets up and tears down a non-bare git repo.

    Yields:
        tuple: (
            source_workdir_path,
            parent_dir_path,
            commits_from_json,
        
    """
    parent_dir_path = init_chm_test_session

    # Create source workdir
    source_workdir_path = create_dir(
        full_path=os.path.join(parent_dir_path, SOURCE_WORKDIR),
        on_conflict='replace'
    )

    # Create and initiallize source repo
    repo = Repo.init(source_workdir_path)

    # Make the commits
    commits = make_commits(repo)

    yield (
        source_workdir_path,
        parent_dir_path,
        commits,
    )

    # Delete the source repo directory
    delete_dir(source_workdir_path)


@pytest.fixture
def non_git_repo(init_source_repo):
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

"""
Fixtures used throughout the test suite

Fixtures:
    init_chm_test_session()
    init_source_repo(init_chm_test_session)
    non_git_repo(init_source_repo)
    dest_repo_master(non_git_repo)
    dest_repo_feature(dest_repo_master)
"""
import os
import tempfile

from git import Repo
import pytest

from app.utils import create_dir, delete_dir
from tests.utils import (
    FEATURE_BRANCH,
    load_commit_data,
    make_commits,
)


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
    commits = make_commits(
        repo=repo,
        commits_data=load_commit_data()
    )

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


@pytest.fixture
def dest_repo_master(non_git_repo):
    """Creates a non empty git repo."""
    repo = Repo.init(non_git_repo)

    # Create and commit some dummy files
    # and make entries to .gitchmirror
    commits_data = load_commit_data()
    make_commits(
        repo=repo,
        commits_data=commits_data[:2],  # First 2 commits only
        has_mirror=True
    )

    # Create new branch (but do not check out)
    repo.create_head(FEATURE_BRANCH)

    yield repo

    # Make sure to check out master before deleting other branches
    if repo.active_branch.name != 'master':
        repo.heads.master.checkout()

    # Delete branches except 'master' and FEATURE_BRANCH
    for branch in repo.branches:
        if branch.name not in ['master', FEATURE_BRANCH]:
            repo.delete_head(branch)


@pytest.fixture
def dest_repo_feature(dest_repo_master):
    """Checks out FEATURE_BRANCH branch in non empty git repo."""
    repo = dest_repo_master
    for branch in repo.branches:
        if branch.name == FEATURE_BRANCH:
            branch.checkout()

    # Create and commit some dummy files
    # and make entries to .gitchmirror
    commits_data = load_commit_data()
    make_commits(
        repo=repo,
        commits_data=commits_data[2:4],  # Commits 3 and 4
        has_mirror=True
    )

    yield repo
    repo.heads.master.checkout()

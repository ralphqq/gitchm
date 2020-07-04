"""
Fixtures used throughout the test suite

Fixtures:
    init_chm_test_session()
    init_source_repo(init_chm_test_session)
    src_repo(init_source_repo)
    iter_commits(init_source_repo)
    empty_iter_commits()
    non_git_repo(init_source_repo)
    dest_repo_no_tree(non_git_repo)
    dest_repo_tree(dest_repo_no_tree)
    dest_repo_mirror_master(non_git_repo)
    dest_repo_mirror_feature(dest_repo_mirror_master)
"""
import os
import tempfile

from git import Repo
import pytest

from gitchm.utils import create_dir, delete_dir
from tests.utils import (
    DEST_FEATURE_COMMITS,
    DEST_MASTER_COMMITS,
    FEATURE_BRANCH,
    load_commit_data,
    load_iter_commits,
    make_commits,
    read_gitchm,
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
def src_repo(init_source_repo):
    src_workdir = init_source_repo[0]
    return Repo(src_workdir)


@pytest.fixture
def iter_commits(init_source_repo):
    """Returns a generator of Commit objects."""
    source_repo_path, _, _ = init_source_repo
    repo = Repo(source_repo_path)
    return repo.iter_commits('master')


@pytest.fixture
def empty_iter_commits():
    """Generator of empty list."""
    def empty_list_gen():
        for p in []:
            yield p
    return empty_list_gen()


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
def dest_repo_no_tree(non_git_repo):
    """Creates a git repo but without a working tree head."""
    repo = Repo.init(non_git_repo)
    yield repo


@pytest.fixture
def dest_repo_tree(dest_repo_no_tree):
    """Creates repo with working tree head at branch master."""
    repo = dest_repo_no_tree

    # Create and commit a file
    fpath = os.path.join(repo.working_dir, 'something.txt')
    with open(fpath, 'w') as f:
        f.write(f'Mundul vult decipi, ergo decipiatur.')
    repo.index.add([fpath])
    repo.index.commit('Dummy commit')

    yield repo


@pytest.fixture
def dest_repo_mirror_master(non_git_repo, src_repo):
    """Creates a mirror repo with commits in master."""
    repo = Repo.init(non_git_repo)

    # Reflect commits #1 and #2 into master
    commits_data = load_iter_commits(src_repo)
    make_commits(
        repo=repo,
        commits_data=commits_data[:DEST_MASTER_COMMITS],
        has_mirror=True
    )

    # Create new branch (but do not check out)
    repo.create_head(FEATURE_BRANCH)

    yield repo

    # Cleanup step

    # Check first if dest repo workdir still exists
    # since sometimes, it can be deleted by another fixture
    if os.path.exists(repo.working_dir):
        if repo.active_branch.name != 'master':
            # Make sure to check out master before deleting other branches
            repo.heads.master.checkout(force=True)

        # Delete branches except 'master' and FEATURE_BRANCH
        for branch in repo.branches:
            if branch.name not in ['master', FEATURE_BRANCH]:
                repo.delete_head(branch)


@pytest.fixture
def dest_repo_mirror_feature(dest_repo_mirror_master, src_repo):
    """Extends dest_repo_mirror_master by making commits in FEATURE_BRANCH."""
    repo = dest_repo_mirror_master
    for branch in repo.branches:
        if branch.name == FEATURE_BRANCH:
            branch.checkout()

    # Reflect commits #3 and #4 to feature
    commits_data = load_iter_commits(src_repo)
    make_commits(
        repo=repo,
        commits_data=commits_data[DEST_MASTER_COMMITS:DEST_FEATURE_COMMITS],
        has_mirror=True
    )
    yield repo

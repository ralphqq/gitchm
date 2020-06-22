"""
Fixtures used to test mirror ops

Fixtures:
    chm(init_source_repo)
    iter_commits(chm)
    dest_repo_master(non_git_repo)
    dest_repo_feature(dest_repo_master)
    chm_dest_master(dest_repo_master, init_source_repo)
    chm_dest_feature(dest_repo_feature, init_source_repo)
"""
import os

from git import Repo
import pytest

from app.mirror import CommitHistoryMirror
from app.utils import delete_dir
from tests.utils import FEATURE_BRANCH


@pytest.fixture
def chm(init_source_repo):
    """Initializes CommitHistoryMirror session."""
    source_repo_path, parent_dir_path, commit_data = init_source_repo
    mirror = CommitHistoryMirror(source_repo_path)
    yield {
        'mirror': mirror,
        'source_workdir': source_repo_path,
        'parent_dir': parent_dir_path,
        'commits': commit_data,
    }

    # Delete dest working dir
    delete_dir(mirror.dest_repo.working_dir)


@pytest.fixture
def iter_commits(chm):
    """Returns a generator of Commit objects."""
    m = chm['mirror']
    return m.source_repo.iter_commits('master')


@pytest.fixture
def dest_repo_master(non_git_repo):
    """Creates a non empty git repo."""
    repo = Repo.init(non_git_repo)

    # Create and commit a dummy file
    dummy_file = 'dummy.txt'
    dummy_file_path = os.path.join(repo.working_dir, dummy_file)
    with open(dummy_file_path, 'w') as f:
        f.write('Mundus vult decipi, ergo decipiatur.')
    repo.index.add(dummy_file_path)
    repo.index.commit('Add new file')

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
    yield repo
    repo.heads.master.checkout()


@pytest.fixture
def chm_dest_master(dest_repo_master, init_source_repo):
    """CHM session with master checked out in dest repo."""
    dest_repo = dest_repo_master
    source_repo_path, _, _ = init_source_repo
    mirror = CommitHistoryMirror(
        source_workdir=source_repo_path,
        dest_workdir=dest_repo.working_dir
    )
    return {'mirror': mirror}


@pytest.fixture
def chm_dest_feature(dest_repo_feature, init_source_repo):
    """CHM session with branch feature checked out in dest repo."""
    dest_repo = dest_repo_feature
    source_repo_path, _, _ = init_source_repo
    mirror = CommitHistoryMirror(
        source_workdir=source_repo_path,
        dest_workdir=dest_repo.working_dir
    )
    return {'mirror': mirror}

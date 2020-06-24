"""
Fixtures used to test mirror ops

Fixtures:
    chm(init_source_repo)
    iter_commits(chm)
    chm_dest_tree(dest_repo_tree, init_source_repo)
    chm_dest_master(dest_repo_mirror_master, init_source_repo)
    chm_dest_feature(dest_repo_mirror_feature, init_source_repo)
"""
import os

from git import Repo
import pytest

from app.mirror import CommitHistoryMirror
from app.utils import delete_dir


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


# All fixtures below need to be refactored

@pytest.fixture
def chm_dest_tree(dest_repo_tree, init_source_repo):
    """CHM session with dest repo that has no tree."""
    dest_repo = dest_repo_tree
    source_repo_path, _, _ = init_source_repo
    mirror = CommitHistoryMirror(
        source_workdir=source_repo_path,
        dest_workdir=dest_repo.working_dir
    )
    return {'mirror': mirror}


@pytest.fixture
def chm_dest_master(dest_repo_mirror_master, init_source_repo):
    """CHM session with master checked out in dest repo."""
    dest_repo = dest_repo_mirror_master
    source_repo_path, _, _ = init_source_repo
    mirror = CommitHistoryMirror(
        source_workdir=source_repo_path,
        dest_workdir=dest_repo.working_dir
    )
    return {'mirror': mirror}


@pytest.fixture
def chm_dest_feature(dest_repo_mirror_feature, init_source_repo):
    """CHM session with branch feature checked out in dest repo."""
    dest_repo = dest_repo_mirror_feature
    source_repo_path, _, _ = init_source_repo
    mirror = CommitHistoryMirror(
        source_workdir=source_repo_path,
        dest_workdir=dest_repo.working_dir
    )
    return {'mirror': mirror}

"""
Fixtures used to test mirror ops

Fixtures:
    chm(init_source_repo)
    iter_commits(chm)
    init_dest_repo(chm)
"""
import pytest

from app.mirror import CommitHistoryMirror
from app.utils import delete_dir


@pytest.fixture(scope='class')
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
def init_dest_repo(chm):
    """Ensures that dest repo's branches get torn down."""
    m = chm['mirror']
    repo = m.dest_repo
    yield chm

    # Make sure master branch is checked out
    if repo.active_branch.name != 'master':
        repo.heads.master.checkout()

    for branch in m.dest_repo.branches:
        if branch.name != 'master':
            # Delete all branches except master
            repo.delete_head(branch)

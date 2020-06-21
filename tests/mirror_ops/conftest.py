import pytest

from app.mirror import CommitHistoryMirror


@pytest.fixture(scope='class')
def chm(init_source_repo):
    """Initializes CommitHistoryMirror session."""
    source_repo_path, parent_dir_path, commit_data = init_source_repo
    mirror = CommitHistoryMirror(source_repo_path)
    return {
        'mirror': mirror,
        'source_workdir': source_repo_path,
        'parent_dir': parent_dir_path,
        'commits': commit_data,
    }


@pytest.fixture
def iter_commits(chm):
    """Returns a generator of Commit objects."""
    m = chm['mirror']
    return m.source_repo.iter_commits('master')

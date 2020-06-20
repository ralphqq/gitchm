import pytest

from app.mirror import CommitHistoryMirror


# Module-wide Fixtures
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


# Tests

class TestMirrorOpsReflect:
    pass

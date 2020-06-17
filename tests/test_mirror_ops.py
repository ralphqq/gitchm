import pytest


class TestMirrorOps:

    @pytest.fixture(scope='class')
    def chm(self, init_source_repo):
        """Initializes CommitHistoryMirror session."""
        source_repo_path, parent_dir_path, commit_data = init_source_repo
        mirror = CommitHistoryMirror(source_repo_path)
        return {
            'mirror': mirror,
            'source_workdir': source_repo_path,
            'parent_dir': parent_dir_path,
            'commits': commit_data,
        }

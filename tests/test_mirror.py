import os

from git import Repo
import pytest

from app.mirror import CommitHistoryMirror


class TestSourceRepoAccess:

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

    def test_source_repo_access(self, chm):
        mirror = chm['mirror']
        all_commits = list(mirror.source_repo.iter_commits('master'))
        source_repo_name = os.path.split(chm['source_workdir'])[-1]

        assert len(all_commits) == len(chm['commits'])
        assert mirror.source_workdir == chm['source_workdir']
        assert mirror.source_repo_name == source_repo_name
        assert mirror.parent_dir == chm['parent_dir']

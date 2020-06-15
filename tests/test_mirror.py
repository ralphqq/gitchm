from git import Repo
import pytest

from app.mirror import CommitHistoryMirror


class TestSourceRepoAccess:

    @pytest.fixture(scope='class')
    def setup_mirror(self, init_source_repo):
        source_repo_path, commit_data = init_source_repo
        mirror = CommitHistoryMirror(source_repo_path)
        return mirror, commit_data

    def test_source_repo_access(self, setup_mirror):
        mirror, commit_data = setup_mirror
        all_commits = list(mirror.source_repo.iter_commits('master'))
        assert len(all_commits) == len(commit_data)

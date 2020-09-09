import pytest

from gitchm.mirror import CommitHistoryMirror


class TestMirrorOverallInit:
    @pytest.fixture
    def mock_init_repos(self, mocker):
        """Mocks the repo _init methods called in constructor."""
        mocker.patch.object(CommitHistoryMirror, "_init_source_repo")
        mocker.patch.object(CommitHistoryMirror, "_init_empty_dest_repo")
        mocker.patch.object(CommitHistoryMirror, "_init_existing_dest_repo")

    def test_mirror_init_with_no_dest_workdir(self, mock_init_repos):
        some_dir = "/tmp/foo/bar"
        mirror = CommitHistoryMirror(some_dir)

        assert mirror.source_workdir == some_dir
        assert mirror._init_source_repo.called
        assert mirror._init_empty_dest_repo.called
        assert not mirror._init_existing_dest_repo.called
        assert not mirror.prior_dest_exists
        assert mirror.dest_prefix == "mirror"

    def test_mirror_init_with_dest_workdir(self, mock_init_repos):
        some_dir = "/tmp/foo/bar"
        some_other_dir = "/tmp/spam/eggs"
        mirror = CommitHistoryMirror(some_dir, some_other_dir)

        assert mirror.source_workdir == some_dir
        assert mirror._init_source_repo.called
        assert not mirror._init_empty_dest_repo.called
        assert mirror._init_existing_dest_repo.called_once_with(some_other_dir)

    def test_mirror_init_with_same_dest_workdir(self, mock_init_repos):
        some_dir = "/tmp/foo/bar"
        with pytest.raises(ValueError):
            CommitHistoryMirror(some_dir, some_dir)

    def test_mirror_init_with_dest_prefix(self, mock_init_repos):
        some_dir = "/tmp/foo/bar"
        dest_prefix = "another-prefix"
        mirror = CommitHistoryMirror(some_dir, prefix=dest_prefix)
        assert mirror.dest_prefix == dest_prefix

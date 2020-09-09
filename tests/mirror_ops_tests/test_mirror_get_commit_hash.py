from git.exc import GitError
import pytest

from tests.utils import FEATURE_BRANCH


class TestGetCommitHash:
    @pytest.mark.parametrize(
        "repo_name,branch",
        [
            ("source", "master"),
            ("dest", "master"),
            ("dest", FEATURE_BRANCH),
        ],
    )
    def test_get_commit_hashes(self, repo_name, branch, chm_dest_feature):
        m = chm_dest_feature["mirror"]
        repo = getattr(m, f"{repo_name}_repo")
        if repo_name == "dest":
            m._set_active_dest_branch(branch)

        hashes = m._get_commit_hashes(repo_name, branch)
        commits = list(repo.iter_commits(branch))

        assert len(hashes) == len(commits)

    def test_incorrect_repo_name(self, chm_dest_feature):
        m = chm_dest_feature["mirror"]
        with pytest.raises(ValueError):
            m._get_commit_hashes("non-existent")

    @pytest.mark.parametrize(
        "repo_name,branch",
        [
            ("source", "x-x"),
            ("dest", "x-x"),
        ],
    )
    def test_invalid_branch(self, repo_name, branch, chm_dest_feature):
        m = chm_dest_feature["mirror"]
        with pytest.raises(GitError):
            m._get_commit_hashes(repo_name, branch)

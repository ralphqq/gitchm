from git import Head, Repo
import pytest

from tests.utils import FEATURE_BRANCH


NEW_BRANCH = "new-branch"


class TestSetDestBranch:
    def test_target_is_active(self, chm_dest_feature, mocker):
        mocker.patch.object(Head, "checkout")
        m = chm_dest_feature["mirror"]
        m._set_active_dest_branch(FEATURE_BRANCH)
        assert not Head.checkout.called
        assert m.dest_head_commit is None

    def test_target_is_not_active(self, chm_dest_master, mocker):
        mocker.patch.object(Repo, "heads")
        m = chm_dest_master["mirror"]
        m._set_active_dest_branch(FEATURE_BRANCH)
        assert m.dest_repo.active_branch.name == FEATURE_BRANCH
        assert not Repo.heads.called

    def test_switch_to_new_branch_from_master(self, chm_dest_master, mocker):
        m = chm_dest_master["mirror"]
        orig_num_branches = len(m.dest_repo.branches)
        m._set_active_dest_branch(NEW_BRANCH)
        assert m.dest_repo.active_branch.name == NEW_BRANCH
        assert len(m.dest_repo.branches) == orig_num_branches + 1

    def test_switch_to_new_branch_from_feature(self, chm_dest_feature, mocker):
        m = chm_dest_feature["mirror"]
        orig_num_branches = len(m.dest_repo.branches)
        m._set_active_dest_branch(NEW_BRANCH)
        assert m.dest_repo.active_branch.name == NEW_BRANCH
        assert len(m.dest_repo.branches) == orig_num_branches + 1

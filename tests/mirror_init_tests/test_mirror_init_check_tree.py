import pytest


class TestCheckTreeState:
    @pytest.fixture
    def mirror(self, modified_chm):
        return modified_chm["mirror"]

    def test_check_dest_no_tree(self, mirror, dest_repo_no_tree):
        mirror.dest_repo = dest_repo_no_tree
        mirror._check_tree_state()
        assert not mirror.dest_has_tree

    def test_check_dest_tree(self, mirror, dest_repo_tree):
        mirror.dest_repo = dest_repo_tree
        mirror._check_tree_state()
        assert mirror.dest_has_tree

    def test_check_dest_mirror_master(self, mirror, dest_repo_mirror_master):
        mirror.dest_repo = dest_repo_mirror_master
        mirror._check_tree_state()
        assert mirror.dest_has_tree

    def test_check_dest_mirror_feature(self, mirror, dest_repo_mirror_feature):
        mirror.dest_repo = dest_repo_mirror_feature
        mirror._check_tree_state()
        assert mirror.dest_has_tree

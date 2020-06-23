import pytest


class TestCheckTreeAndMirror:

    @pytest.fixture
    def mirror(self, modified_chm):
        return modified_chm['mirror']

    def test_check_dest_no_tree(self, mirror, dest_repo_no_tree):
        mirror.dest_repo = dest_repo_no_tree
        mirror._check_dest_tree_and_mirror()
        assert not mirror.dest_has_tree
        assert not mirror.dest_is_mirror

    def test_check_dest_tree(self, mirror, dest_repo_tree):
        mirror.dest_repo = dest_repo_tree
        mirror._check_dest_tree_and_mirror()
        assert mirror.dest_has_tree
        assert not mirror.dest_is_mirror

    def test_check_dest_mirror_master(self, mirror, dest_repo_mirror_master):
        mirror.dest_repo = dest_repo_mirror_master
        mirror._check_dest_tree_and_mirror()
        assert mirror.dest_has_tree
        assert mirror.dest_is_mirror

    def test_check_dest_mirror_feature(self, mirror, dest_repo_mirror_feature):
        mirror.dest_repo = dest_repo_mirror_feature
        mirror._check_dest_tree_and_mirror()
        assert mirror.dest_has_tree
        assert mirror.dest_is_mirror

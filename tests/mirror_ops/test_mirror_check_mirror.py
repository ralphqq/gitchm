import pytest

from tests.utils import (
    DEST_FEATURE_COMMITS,
    DEST_MASTER_COMMITS,
)


class TestMirrorState:

    def test_check_empty_repo(self, chm):
        m = chm['mirror']
        with pytest.raises(ValueError):
            m._check_mirror_state()

    def test_check_repo_with_tree(self, chm_dest_tree):
        m = chm_dest_tree['mirror']
        m._check_mirror_state()
        assert not m.dest_is_mirror
        assert not m.dest_commit_hashes

    def test_check_repo_mirror_in_master(self, chm_dest_master):
        m = chm_dest_master['mirror']
        m._check_mirror_state()
        assert m.dest_is_mirror
        assert len(m.dest_commit_hashes) == DEST_MASTER_COMMITS

    def test_check_repo_mirror_in_feature(self, chm_dest_feature):
        m = chm_dest_feature['mirror']
        m._check_mirror_state()
        assert m.dest_is_mirror
        assert len(m.dest_commit_hashes) == DEST_FEATURE_COMMITS

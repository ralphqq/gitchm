from git import Head, Repo
import pytest


NEW_BRANCH = 'new-branch'


class TestSetDestBranch:

    def test_branch_is_already_active_master(self, init_dest_repo, mocker):
        mocker.patch.object(Head, 'checkout')
        m = init_dest_repo['mirror']
        m._set_active_dest_branch('master')
        assert not Head.checkout.called

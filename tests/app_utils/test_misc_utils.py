"""
Other utils tests

Classes:
    TestMiscUtils
"""
import os

from git import Actor
import pytest

from app.exc import IncompleteCommitDetails
from app.utils import (
    clean_dict,
    create_actor,
)


class TestMiscUtils:

    def test_dict_cleanup(self):
        orig_dict = {'a': 1, 'b': None, 'c': '', 'd': 0}
        new_dict = clean_dict(orig_dict)
        assert 'a' in new_dict
        assert 'b' not in new_dict
        assert 'c' in new_dict
        assert 'd' in new_dict

    @pytest.mark.parametrize(
        'name,email',
        [
            ('Name', 'name@email.com'),
            ('Name', ''),
            ('', 'name@email.com'),
            ('', ''),
        ]
    )
    def test_create_actor(self, name, email):
        if not name and not email:
            with pytest.raises(IncompleteCommitDetails):
                create_actor(name=name, email=email)

        else:
            actor = create_actor(name=name, email=email)
            assert isinstance(actor, Actor)

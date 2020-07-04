"""
Other utils tests

Classes:
    TestMiscUtils
"""
from datetime import datetime
import os
import re

from git import Actor
import pytest

from gitchm.exc import IncompleteCommitDetails
from gitchm.utils import (
    clean_dict,
    create_actor,
    format_stats,
    to_datetime,
)


EXPECTED_DT1 = datetime(2020, 6, 28)    # No time of day
EXPECTED_DT2 = datetime(2020, 6, 28, 15, 30)    # No seconds
EXPECTED_DT3 = datetime(2020, 6, 28, 15, 30, 10)    # With seconds
EXPECTED_TS1 = EXPECTED_DT1.timestamp()


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

    @pytest.mark.parametrize('date_str,output,expected_result',[
        ('2020/6/28', 'dt', EXPECTED_DT1),
        ('2020/6/28', 'ts', EXPECTED_TS1),
        ('2020/06/28', 'dt', EXPECTED_DT1),
        ('6/28/2020', 'dt', EXPECTED_DT1),
        ('2020-6-28', 'dt', EXPECTED_DT1),
        ('2020-06-28', 'dt', EXPECTED_DT1),
        ('June 28, 2020', 'dt', EXPECTED_DT1),
        ('28 June 2020', 'dt', EXPECTED_DT1),
        ('June 28, 2020 3:30 PM', 'dt', EXPECTED_DT2),
        ('28 June 2020 3:30 p.m.', 'dt', EXPECTED_DT2),
        ('2020-6-28 15:30', 'dt', EXPECTED_DT2),
        ('2020-6-28 15:30:10', 'dt', EXPECTED_DT3),
    ])
    def test_valid_date_str(self, date_str, output, expected_result):
        assert to_datetime(date_str, output) == expected_result

    def test_invalid_date_output(self):
        with pytest.raises(ValueError):
            to_datetime('2020/6/28', 'xx')

    def test_invalid_date_input(self):
        with pytest.raises(ValueError):
            to_datetime('sla;khfa')

    def test_format_stats(self):
        stats = {'a': 12, 'b': 34, 'c': 0}
        result = format_stats(stats)

        assert isinstance(result, str)
        assert len(re.findall(r'\w+: \d+ commits', result)) == len(stats)

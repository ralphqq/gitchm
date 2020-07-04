from datetime import datetime
import os

import pytest

from gitchm.init import date_to_ts, path_parser


EXPECTED_DT1 = datetime(2020, 6, 28)    # No time of day
EXPECTED_DT2 = datetime(2020, 6, 28, 15, 30)    # No seconds
EXPECTED_DT3 = datetime(2020, 6, 28, 15, 30, 10)    # With seconds
EXPECTED_TS1 = EXPECTED_DT1.timestamp()
EXPECTED_TS2 = EXPECTED_DT2.timestamp()
EXPECTED_TS3 = EXPECTED_DT3.timestamp()

REAL_DIR = os.getcwd()
FAKE_DIR = os.path.join(REAL_DIR, 'foobarspambaz123')


class TestInitParsers:

    @pytest.mark.parametrize('input,output', [
        ('2020-6-28', EXPECTED_TS1),
        ('2020-06-28', EXPECTED_TS1),
        ('2020-6-28 15:30', EXPECTED_TS2),
        ('2020-6-28 15:30:10', EXPECTED_TS3),
    ])
    def test_date_to_ts_transformer(self, input, output):
        result = date_to_ts.apply(input)
        assert isinstance(result, int)
        assert result == output

    @pytest.mark.parametrize('input,output', [
        (REAL_DIR, True),
        (FAKE_DIR, False),
    ])
    def test_path_parser_validator(self, input, output):
        result = path_parser.apply(input)
        assert isinstance(result, bool)
        assert result == output

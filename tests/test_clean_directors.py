import pytest
from get_stakeholder_data.script.clean_directors import clean_directors, normalize_date


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("２０００年１月１日生", "2000-01-01"),
        ("1990年12月5日", "1990-12-05"),
        ("1987年7月20日", "1987-07-20"),
    ],
)
def test_normalize_date_valid(input_str, expected):
    assert normalize_date(input_str) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "令和五年八月",
        "abc",
        "",
        None,
    ],
)
def test_normalize_date_invalid(input_str):
    assert normalize_date(input_str) is None

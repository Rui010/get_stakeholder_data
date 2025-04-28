import pytest
from get_stakeholder_data.script.clean_directors import (
    clean_directors,
    normalize_date,
    normalize_name,
)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("２０００年１月１日生", "2000-01-01"),
        ("1990年12月5日", "1990-12-05"),
        ("1987年7月20日", "1987-07-20"),
        ("(1947年１月17日生)", "1947-01-17"),
        ("（1964年２月16日生）", "1964-02-16"),
        ("1933年８月28日生", "1933-08-28"),
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
        "記載なし",
        None,
    ],
)
def test_normalize_date_invalid(input_str):
    assert normalize_date(input_str) is None


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("吉 野 正 己", "吉野正己"),
        ("Amy Shigemi Hatta", "Amy Shigemi Hatta"),
        ("Didier Leroy (ディディエ ルロワ)", "Didier Leroy"),
        ("三輪 正俊", "三輪正俊"),
        ("三谷 和歌子（戸籍上の氏名は赤松和歌子）", "三谷和歌子"),
        ("ヴー ヴァン チュン", "ヴーヴァンチュン"),
        ("三 井 田  健   みいだ たけし", "三井田健みいだたけし"),
    ],
)
def test_normalize_name_valid(input_str, expected):
    assert normalize_name(input_str) == expected


@pytest.mark.parametrize(
    "input_str",
    [
        "",
        " ",
        None,
    ],
)
def test_normalize_name_invalid(input_str):
    assert normalize_name(input_str) is None

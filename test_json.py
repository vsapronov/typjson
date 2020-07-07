from jsoner import *
from typing import *
from dataclasses import *
from pytest import *
from decimal import *
from datetime import *

def check_serialization(typ, data, the_json):
    assert to_json(data) == the_json
    assert from_json(typ, the_json) == data


def test_int_serialization():
    check_serialization(int, 3, '3')


def test_int_deserialization_wrong_type():
    with raises(JsonerException):
        from_json(int, '"3"')


def test_float_serialization():
    check_serialization(float, 1.23, '1.23')


# def test_decimal_serialization():
#     check_serialization(Decimal, Decimal(1.23), '1.23')


def test_str_serialization():
    check_serialization(str, 'bla', '"bla"')


def test_bool_serialization():
    check_serialization(bool, True, 'true')


def test_none_serialization():
    check_serialization(NoneType, None, 'null')


def test_date_serialization():
    check_serialization(date, date(year=2020, month=1, day=1), '"2020-01-01"')


def test_none_deserialization_wrong_value():
    with raises(JsonerException):
        from_json(NoneType, '"bla"')


def test_list_serialization():
    check_serialization(List[int], [2, 3], '[2, 3]')


def test_list_of_date_serialization():
    check_serialization(List[date], [date(year=2020, month=1, day=2)], '["2020-01-02"]')


@dataclass
class TheClass:
    string_field: str
    int_field: int


def test_class_serialization():
    check_serialization(TheClass, TheClass('bla', 123), '{"string_field": "bla", "int_field": 123}')


def test_class_serialization_wrong_field_type():
    with raises(JsonerException):
        check_serialization(TheClass, TheClass('bla', 'wrong'), '{"string_field": "bla", "int_field": "wrong"}')

from jsoner import *
from typing import *
from dataclasses import *
from pytest import *
from decimal import *
from datetime import *


def check_success(typ, data, json_str):
    assert to_json(data, typ) == json_str
    assert from_json(typ, json_str) == data


def check_type_error(typ, data, json_str):
    with raises(JsonerException):
        to_json(data, typ)
    with raises(JsonerException):
        from_json(typ, json_str)


def test_int_serialization():
    check_success(int, 3, '3')


def test_int_serialization_boolean():
    check_type_error(int, True, 'true')


def test_int_deserialization_wrong_type():
    check_type_error(int, '3', '"3"')


def test_float_serialization_fractional():
    check_success(float, 1.23, '1.23')


def test_float_deserialization_whole():
    assert float(1) == from_json(float, '1')


# def test_decimal_serialization():
#     check_serialization(Decimal, Decimal(1.23), '1.23')


def test_str_serialization():
    check_success(str, 'bla', '"bla"')


def test_serialization_null_safety():
    check_type_error(str, None, 'null')


def test_bool_serialization():
    check_success(bool, True, 'true')


def test_none_serialization():
    check_success(NoneType, None, 'null')


def test_date_serialization():
    check_success(date, date(year=2020, month=1, day=1), '"2020-01-01"')


def test_none_serialization_wrong_type():
    check_type_error(NoneType, 'bla', '"bla"')


def test_list_serialization():
    check_success(List[int], [2, 3], '[2, 3]')


def test_list_of_date_serialization():
    check_success(List[date], [date(year=2020, month=1, day=2)], '["2020-01-02"]')


def test_dict_serialization():
    check_success(Dict[str, date], {'key': date(year=2020, month=1, day=2)}, '{"key": "2020-01-02"}')


def test_dict_serialization_wrong_key_type():
    check_type_error(Dict[int, date], {2: date(year=2020, month=1, day=2)}, '{"2": "2020-01-02"}')


def test_optional_serialization_none():
    check_success(Optional[int], None, 'null')


def test_optional_serialization_some():
    check_success(Optional[int], 123, '123')


def test_union_primitive_serialization():
    check_success(Union[str, int], 'bla', '"bla"')
    check_success(Union[str, int], 3, '3')


def test_union_wrong_type():
    check_type_error(Union[str, int], True, 'true')


@dataclass
class TheClass:
    string_field: str
    int_field: int


def test_class_serialization():
    check_success(TheClass, TheClass('bla', 123), '{"string_field": "bla", "int_field": 123}')


def test_class_serialization_wrong_type():
    check_type_error(TheClass, TheClass('bla', 'wrong'), '{"string_field": "bla", "int_field": "wrong"}')


def test_untyped_list():
    json_str = to_json([date(year=2020, month=1, day=2)])
    assert json_str == '["2020-01-02"]'

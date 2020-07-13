from jsoner import *
from typing import *
from dataclasses import *
from pytest import *
from decimal import *
from datetime import *


def check_success(typ, data, json_str):
    assert dumps(data, typ) == json_str
    assert loads(typ, json_str) == data


def check_type_error(typ, data, json_str):
    with raises(JsonerException):
        dumps(data, typ)
    with raises(JsonerException):
        loads(typ, json_str)


def test_int():
    check_success(int, 3, '3')


def test_int_boolean():
    check_type_error(int, True, 'true')


def test_int_wrong_type():
    check_type_error(int, '3', '"3"')


def test_float():
    check_success(float, 1.23, '1.23')


def test_float_int_json():
    assert float(1) == loads(float, '1')


def test_str():
    check_success(str, 'bla', '"bla"')


def test_null_safety():
    check_type_error(str, None, 'null')


def test_bool():
    check_success(bool, True, 'true')


def test_none():
    check_success(NoneType, None, 'null')


def test_date():
    check_success(date, date(year=2020, month=1, day=1), '"2020-01-01"')


def test_none_wrong_type():
    check_type_error(NoneType, 'bla', '"bla"')


def test_generic_list():
    check_success(List[int], [2, 3], '[2, 3]')


def test_generic_list_of_date():
    check_success(List[date], [date(year=2020, month=1, day=2)], '["2020-01-02"]')


def test_generic_dict():
    check_success(Dict[str, date], {'key': date(year=2020, month=1, day=2)}, '{"key": "2020-01-02"}')


def test_generic_dict_wrong_key_type():
    check_type_error(Dict[int, date], {2: date(year=2020, month=1, day=2)}, '{"2": "2020-01-02"}')


def test_optional_none():
    check_success(Optional[int], None, 'null')


def test_optional_some():
    check_success(Optional[int], 123, '123')


def test_union_primitives():
    check_success(Union[str, int], 'bla', '"bla"')
    check_success(Union[str, int], 3, '3')


def test_union_wrong_type():
    check_type_error(Union[str, int], True, 'true')


@dataclass
class TheClass:
    string_field: str
    int_field: int


def test_dataclass():
    check_success(TheClass, TheClass('bla', 123), '{"string_field": "bla", "int_field": 123}')


def test_dataclass_wrong_field_type():
    check_type_error(TheClass, TheClass('bla', 'wrong'), '{"string_field": "bla", "int_field": "wrong"}')


def test_untyped_list():
    json = dumps([date(year=2020, month=1, day=2)])
    assert json == '["2020-01-02"]'


def test_untyped_dict():
    json = dumps({"key": date(year=2020, month=1, day=2)})
    assert json == '{"key": "2020-01-02"}'

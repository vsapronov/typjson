from jsoner import *
from typing import *
from dataclasses import *
from pytest import *

def check_serialization(typ, data, the_json):
    assert to_json(data) == the_json
    assert from_json(typ, the_json) == data


def test_int_serialization():
    check_serialization(int, 3, '3')


def test_int_deserialization_wrong_type():
    with raises(JsonerException):
        from_json(int, '3')


def test_str_serialization():
    check_serialization(str, 'bla', '"bla"')


def test_none_serialization():
    check_serialization(Optional[str], None, 'null')


def test_list_serialization():
    check_serialization(List[int], [2, 3], '[2, 3]')


# class TheClass:
#     def __init__(self, string_field: str, int_field: int):
#         self.string_field = string_field
#         self.int_field = int_field
#
#     def __eq__(self, other):
#         if isinstance(other, self.__class__):
#             return self.__dict__ == other.__dict__
#         else:
#             return False


@dataclass
class TheClass:
    string_field: str
    int_field: int


def test_class_serialization():
    check_serialization(TheClass, TheClass('bla', 123), '{"string_field": "bla", "int_field": 123}')


def test_class_serialization_wrong_field_type():
    with raises(JsonerException):
        check_serialization(TheClass, TheClass('bla', 'wrong'), '{"string_field": "bla", "int_field": "wrong"}')


# def test_none2_serialization():
#     check_serialization(str, None, 'null')

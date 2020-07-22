from typ.json import *
from typ.typing import *
from typ.encoding import *
from typing import *
from dataclasses import *
from pytest import *
from decimal import *
from datetime import *
from uuid import *


def check_success(typ, data, json_str):
    assert dumps(data, typ) == json_str
    assert loads(typ, json_str) == data


def check_type_error(typ, data, json_str):
    with raises(JsonError):
        dumps(data, typ)
    with raises(JsonError):
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


def test_decimal():
    check_success(Decimal, Decimal('1.23'), '1.23')


def test_str():
    check_success(str, 'bla', '"bla"')


def test_char():
    check_success(char, char('x'), '"x"')


def test_null_safety():
    check_type_error(str, None, 'null')


def test_bool():
    check_success(bool, True, 'true')


def test_none():
    check_success(NoneType, None, 'null')


def test_none_wrong_type():
    check_type_error(NoneType, 'bla', '"bla"')


def test_date():
    check_success(date, date(year=2020, month=1, day=1), '"2020-01-01"')


def test_datetime():
    check_success(datetime, datetime(year=2020, month=1, day=1, hour=17, minute=45, second=55, tzinfo=timezone.utc), '"2020-01-01T17:45:55+00:00"')


def test_time():
    check_success(time, time(hour=17, minute=45, second=55), '"17:45:55"')


def test_date_wrong_type():
    check_type_error(date, 3, '3')


def test_uuid():
    check_success(UUID, UUID('bd65600d-8669-4903-8a14-af88203add38'), '"bd65600d-8669-4903-8a14-af88203add38"')


def test_generic_list():
    check_success(List[int], [2, 3], '[2, 3]')


def test_generic_list_of_date():
    check_success(List[date], [date(year=2020, month=1, day=2)], '["2020-01-02"]')


def test_generic_dict():
    check_success(Dict[str, date], {'key': date(year=2020, month=1, day=2)}, '{"key": "2020-01-02"}')


def test_generic_dict_wrong_key_type():
    check_type_error(Dict[int, date], {2: date(year=2020, month=1, day=2)}, '{"2": "2020-01-02"}')


def test_generic_tuple():
    check_success(Tuple[str, int], ('bla', 3), '["bla", 3]')


def test_generic_set():
    check_success(Set[date], set([date(year=2020, month=1, day=2)]), '["2020-01-02"]')


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


def test_any():
    check_success(Any, 'bla', '"bla"')


def test_untyped_list():
    json = dumps([date(year=2020, month=1, day=2), 2])
    assert json == '["2020-01-02", 2]'


def test_untyped_dict():
    json = dumps({'key1': date(year=2020, month=1, day=2), 'key2': 'bla'})
    assert json == '{"key1": "2020-01-02", "key2": "bla"}'


def test_untyped_tuple():
    json = dumps((date(year=2020, month=1, day=2), 2))
    assert json == '["2020-01-02", 2]'


def test_untyped_set():
    json = dumps(set([date(year=2020, month=1, day=2)]))
    assert json == '["2020-01-02"]'


def test_load_dump():
    data_before = TheClass('bla', 123)
    with open('temp', 'w') as fp:
        dump(fp, data_before, TheClass)
    with open('temp', 'r') as fp:
        data_after = load(fp, TheClass)
    assert data_before == data_after


def encode_int_custom(encoder, typ, value):
    if typ != int:
        return Unsupported
    check_type(int, value)
    return str(value)


def decode_int_custom(decoder, typ, json_value):
    if typ != int:
        return Unsupported
    check_type(str, json_value)
    return int(json_value)


def test_int_custom():
    assert dumps([3, 4, 5], encoders=[encode_int_custom]) == '["3", "4", "5"]'
    assert loads(List[int], '["3", "4", "5"]', decoders=[decode_int_custom]) == [3, 4, 5]

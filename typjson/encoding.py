from typing import *
import typing_inspect as inspect  # type: ignore
import dataclasses
from datetime import date, datetime, time
from decimal import *
from uuid import *
from typjson.typing import *


class UnsupportedType:
    pass


class JsonerException(Exception):
    pass


def encode_primitive(typ, value):
    if typ not in [int, float, str, bool, NoneType]:
        return UnsupportedType()
    if not type(value) == typ:
        raise JsonerException(f'Type {typ} was expected, found: {value}')
    return value


def decode_primitive(typ, json_value):
    if typ not in [int, Decimal, str, bool, NoneType]:
        return UnsupportedType()
    if not type(json_value) == typ:
        raise JsonerException(f'Type {typ} was expected, found type: {type(json_value)} value: {json_value}')
    return json_value


def encode_char(typ, value):
    if typ != char:
        return UnsupportedType()
    if not type(value) == char:
        raise JsonerException(f'Type {typ} was expected, found: {type(value)}, value: {value}')
    return str(value)


def decode_char(typ, json_value):
    if typ != char:
        return UnsupportedType()
    if not type(json_value) == str:
        raise JsonerException(f'char should be represented as str, found {type(json_value)}, value: {json_value}')
    if len(json_value) != 1:
        raise JsonerException(f'char should be represented with str length 1, found: {json_value}')
    return json_value


def decode_float(typ, json_value):
    if typ != float:
        return UnsupportedType()
    if type(json_value) not in [int, float, Decimal]:
        raise JsonerException(f'Numeric type was expected, found: {type(json_value)}, value: {json_value}')
    return float(json_value)


def encode_decimal(typ, value):
    if typ != Decimal:
        return UnsupportedType()
    if type(value) != typ:
        raise JsonerException(f'Type Decimal was expected, found: {type(value)}, value: {value}')
    return float(value)


def encode_date(typ, value):
    if typ != date:
        return UnsupportedType()
    if not isinstance(value, date):
        raise JsonerException(f'date type expected, found {type(value)}, value: {value}')
    return value.isoformat()


def decode_date(typ, json_value):
    if typ != date:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'date should be represented as str, found {type(json_value)}, value: {json_value}')
    parsed_datetime = datetime.strptime(json_value, "%Y-%m-%d")
    return parsed_datetime.date()


def encode_datetime(typ, value):
    if typ != datetime:
        return UnsupportedType()
    if not isinstance(value, datetime):
        raise JsonerException(f'datetime type expected, found {type(value)}, value: {value}')
    return value.isoformat()


def decode_datetime(typ, json_value):
    if typ != datetime:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'datetime should be represented as str, found {type(json_value)}, value: {json_value}')
    parsed = datetime.strptime(json_value, "%Y-%m-%dT%H:%M:%S%z")
    return parsed


def encode_time(typ, value):
    if typ != time:
        return UnsupportedType()
    if not isinstance(value, time):
        raise JsonerException(f'time type expected, found {type(value)}, value: {value}')
    return value.isoformat()


def decode_time(typ, json_value):
    if typ != time:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'time should be represented as str, found {type(json_value)}, value: {json_value}')
    parsed_datetime = datetime.strptime(json_value, "%H:%M:%S")
    return parsed_datetime.time()


def encode_uuid(typ, value):
    if typ != UUID:
        return UnsupportedType()
    if not isinstance(value, UUID):
        raise JsonerException(f'UUID type expected found: {type(value)}, value: {value}')
    return str(value)


def decode_uuid(typ, json_value):
    if typ != UUID:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'UUID should be represented as str, found {type(json_value)}, value: {json_value}')
    return UUID(json_value)


def encode_dataclass(typ, value):
    if not dataclasses.is_dataclass(typ):
        return UnsupportedType()
    return {field.name: encode(value.__dict__[field.name], field.type) for field in dataclasses.fields(typ)}


def decode_dataclass(typ, json_value):
    if not dataclasses.is_dataclass(typ):
        return UnsupportedType()
    ctor_params = {field.name: decode(field.type, json_value[field.name]) for field in dataclasses.fields(typ)}
    value = typ(**ctor_params)
    return value


def encode_generic_list(typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == list):
        return UnsupportedType()
    item_type, = inspect.get_args(typ)
    return [encode(item, item_type) for item in value]


def decode_generic_list(typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == list):
        return UnsupportedType()
    item_type = inspect.get_args(typ)[0]
    return [decode(item_type, item) for item in json_value]


def encode_list(typ, value):
    if typ != list:
        return UnsupportedType()
    return [encode(item, None) for item in value]


def encode_dict(typ, value):
    if typ != dict:
        return UnsupportedType()
    return {item_key: encode(item_value, None) for item_key, item_value in value.items()}


def encode_generic_dict(typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict):
        return UnsupportedType()
    key_type, value_type = inspect.get_args(typ)
    if key_type != str:
        raise JsonerException(f'Dict key type {key_type} is not supported for JSON serializatio, key should be of type str')
    return {key: encode(value, value_type) for (key, value) in value.items()}


def decode_generic_dict(typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict):
        return UnsupportedType()
    key_type, value_type = inspect.get_args(typ)
    if key_type != str:
        raise JsonerException(f'Dict key type {key_type} is not supported for JSON deserialization - key should be str')
    return {key: decode(value_type, value) for (key, value) in json_value.items()}


def encode_union(typ, value):
    if not inspect.is_union_type(typ):
        return UnsupportedType()
    union_types = inspect.get_args(typ)
    for union_type in union_types:
        try:
            return encode(value, union_type)
        except JsonerException:
            pass
    raise JsonerException(f'Value {value} can not be deserialized as {typ}')


def decode_union(typ, json_value):
    if not inspect.is_union_type(typ):
        return UnsupportedType()
    union_types = inspect.get_args(typ)
    for union_type in union_types:
        try:
            return decode(union_type, json_value)
        except JsonerException:
            pass
    raise JsonerException(f'Value {json_value} can not be deserialized as {typ}')


encoders = [
    encode_primitive,
    encode_char,
    encode_decimal,
    encode_date,
    encode_datetime,
    encode_time,
    encode_uuid,
    encode_generic_list,
    encode_generic_dict,
    encode_union,
    encode_dataclass,
    encode_list,
    encode_dict
]

decoders = [
    decode_primitive,
    decode_char,
    decode_float,
    decode_date,
    decode_datetime,
    decode_time,
    decode_uuid,
    decode_generic_list,
    decode_generic_dict,
    decode_union,
    decode_dataclass
]


T = TypeVar('T')


def decode(typ: Type[T], json_value: Any) -> T:
    for decoder in decoders:
        result = decoder(typ, json_value)
        if not isinstance(result, UnsupportedType):
            return result
    raise JsonerException(f'Unsupported type {typ}')


def encode(value: T, typ: Optional[Type[T]] = None):
    typ = typ if typ is not None else type(value)
    for encoder in encoders:
        result = encoder(typ, value)
        if not isinstance(result, UnsupportedType):
            return result
    raise JsonerException(f'Unsupported type {typ}')

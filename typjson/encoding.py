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


def encode_primitive(encoder, typ, value):
    if typ not in [int, float, str, bool, NoneType]:
        return UnsupportedType()
    if not type(value) == typ:
        raise JsonerException(f'Type {typ} was expected, found: {value}')
    return value


def decode_primitive(decoder, typ, json_value):
    if typ not in [int, Decimal, str, bool, NoneType]:
        return UnsupportedType()
    if not type(json_value) == typ:
        raise JsonerException(f'Type {typ} was expected, found type: {type(json_value)} value: {json_value}')
    return json_value


def encode_char(encoder, typ, value):
    if typ != char:
        return UnsupportedType()
    if not type(value) == char:
        raise JsonerException(f'Type {typ} was expected, found: {type(value)}, value: {value}')
    return str(value)


def decode_char(decoder, typ, json_value):
    if typ != char:
        return UnsupportedType()
    if not type(json_value) == str:
        raise JsonerException(f'char should be represented as str, found {type(json_value)}, value: {json_value}')
    if len(json_value) != 1:
        raise JsonerException(f'char should be represented with str length 1, found: {json_value}')
    return json_value


def decode_float(decoder, typ, json_value):
    if typ != float:
        return UnsupportedType()
    if type(json_value) not in [int, float, Decimal]:
        raise JsonerException(f'Numeric type was expected, found: {type(json_value)}, value: {json_value}')
    return float(json_value)


def encode_decimal(encoder, typ, value):
    if typ != Decimal:
        return UnsupportedType()
    if type(value) != typ:
        raise JsonerException(f'Type Decimal was expected, found: {type(value)}, value: {value}')
    return float(value)


def encode_date(encoder, typ, value):
    if typ != date:
        return UnsupportedType()
    if not isinstance(value, date):
        raise JsonerException(f'date type expected, found {type(value)}, value: {value}')
    return value.isoformat()


def decode_date(decoder, typ, json_value):
    if typ != date:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'date should be represented as str, found {type(json_value)}, value: {json_value}')
    parsed_datetime = datetime.strptime(json_value, "%Y-%m-%d")
    return parsed_datetime.date()


def encode_datetime(encoder, typ, value):
    if typ != datetime:
        return UnsupportedType()
    if not isinstance(value, datetime):
        raise JsonerException(f'datetime type expected, found {type(value)}, value: {value}')
    return value.isoformat()


def decode_datetime(decoder, typ, json_value):
    if typ != datetime:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'datetime should be represented as str, found {type(json_value)}, value: {json_value}')
    parsed = datetime.strptime(json_value, "%Y-%m-%dT%H:%M:%S%z")
    return parsed


def encode_time(encoder, typ, value):
    if typ != time:
        return UnsupportedType()
    if not isinstance(value, time):
        raise JsonerException(f'time type expected, found {type(value)}, value: {value}')
    return value.isoformat()


def decode_time(decoder, typ, json_value):
    if typ != time:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'time should be represented as str, found {type(json_value)}, value: {json_value}')
    parsed_datetime = datetime.strptime(json_value, "%H:%M:%S")
    return parsed_datetime.time()


def encode_uuid(encoder, typ, value):
    if typ != UUID:
        return UnsupportedType()
    if not isinstance(value, UUID):
        raise JsonerException(f'UUID type expected found: {type(value)}, value: {value}')
    return str(value)


def decode_uuid(decoder, typ, json_value):
    if typ != UUID:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'UUID should be represented as str, found {type(json_value)}, value: {json_value}')
    return UUID(json_value)


def encode_dataclass(encoder, typ, value):
    if not dataclasses.is_dataclass(typ):
        return UnsupportedType()
    return {field.name: encoder.encode(value.__dict__[field.name], field.type) for field in dataclasses.fields(typ)}


def decode_dataclass(decoder, typ, json_value):
    if not dataclasses.is_dataclass(typ):
        return UnsupportedType()
    ctor_params = {field.name: decoder.decode(field.type, json_value[field.name]) for field in dataclasses.fields(typ)}
    value = typ(**ctor_params)
    return value


def encode_generic_list(encoder, typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == list):
        return UnsupportedType()
    item_type, = inspect.get_args(typ)
    return [encoder.encode(item, item_type) for item in value]


def decode_generic_list(decoder, typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == list):
        return UnsupportedType()
    item_type = inspect.get_args(typ)[0]
    return [decoder.decode(item_type, item) for item in json_value]


def encode_list(encoder, typ, value):
    if typ != list:
        return UnsupportedType()
    return [encoder.encode(item, None) for item in value]


def encode_dict(encoder, typ, value):
    if typ != dict:
        return UnsupportedType()
    return {item_key: encoder.encode(item_value, None) for item_key, item_value in value.items()}


def encode_generic_dict(encoder, typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict):
        return UnsupportedType()
    key_type, value_type = inspect.get_args(typ)
    if key_type != str:
        raise JsonerException(f'Dict key type {key_type} is not supported for JSON serializatio, key should be of type str')
    return {key: encoder.encode(value, value_type) for (key, value) in value.items()}


def decode_generic_dict(decoder, typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict):
        return UnsupportedType()
    key_type, value_type = inspect.get_args(typ)
    if key_type != str:
        raise JsonerException(f'Dict key type {key_type} is not supported for JSON deserialization - key should be str')
    return {key: decoder.decode(value_type, value) for (key, value) in json_value.items()}


def encode_generic_tuple(encoder, typ, value):
    if not inspect.is_tuple_type(typ):
        return UnsupportedType()
    if type(value) != tuple:
        raise JsonerException(f'Expected tuple, found {type(value)}, value: {value}')
    items_types = inspect.get_args(typ)
    if len(items_types) != len(value):
        raise JsonerException(f'Expected tuple of size: {len(items_types)}, found tuple of size: {len(value)}, value: {value}')
    return tuple(map(lambda item, item_type: encoder.encode(item, item_type), value, items_types))


def decode_generic_tuple(decoder, typ, json_value):
    if not inspect.is_tuple_type(typ):
        return UnsupportedType()
    if type(json_value) != list:
        raise JsonerException(f'Expected list, found {type(json_value)}, value: {json_value}')
    items_types = inspect.get_args(typ)
    if len(items_types) != len(json_value):
        raise JsonerException(f'Expected list of size: {len(items_types)}, found tuple of size: {len(json_value)}, value: {json_value}')
    return tuple(map(lambda item, item_type: decoder.decode(item_type, item), json_value, items_types))


def encode_union(encoder, typ, value):
    if not inspect.is_union_type(typ):
        return UnsupportedType()
    union_types = inspect.get_args(typ)
    for union_type in union_types:
        try:
            return encoder.encode(value, union_type)
        except JsonerException:
            pass
    raise JsonerException(f'Value {value} can not be deserialized as {typ}')


def decode_union(decoder, typ, json_value):
    if not inspect.is_union_type(typ):
        return UnsupportedType()
    union_types = inspect.get_args(typ)
    for union_type in union_types:
        try:
            return decoder.decode(union_type, json_value)
        except JsonerException:
            pass
    raise JsonerException(f'Value {json_value} can not be deserialized as {typ}')


T = TypeVar('T')


class Decoder:
    def __init__(self, decoders):
        self.decoders = decoders

    def decode(self, typ: Type[T], json_value: Any) -> T:
        for decoder in self.decoders:
            result = decoder(self, typ, json_value)
            if not isinstance(result, UnsupportedType):
                return result
        raise JsonerException(f'Unsupported type {typ}')


class Encoder:
    def __init__(self, encoders):
        self.encoders = encoders

    def encode(self, value: T, typ: Optional[Type[T]] = None):
        typ = typ if typ is not None else type(value)
        for encoder in self.encoders:
            result = encoder(self, typ, value)
            if not isinstance(result, UnsupportedType):
                return result
        raise JsonerException(f'Unsupported type {typ}')


def decode(typ: Type[T], json_value: Any, decoders=[]):
    return Decoder(decoders).decode(typ, json_value)


def encode(value: T, typ: Optional[Type[T]] = None, encoders=[]):
    return Encoder(encoders).encode(value, typ)

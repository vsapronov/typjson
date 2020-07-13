import json
from typing import *
import typing_inspect as inspect
import dataclasses
import datetime
from datetime import date


NoneType = type(None)


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
    if typ not in [int, str, bool, NoneType]:
        return UnsupportedType()
    if not type(json_value) == typ:
        raise JsonerException(f'Type {typ} was expected, found type: {type(json_value)} value: {json_value}')
    return json_value


def decode_float(typ, json_value):
    if typ != float:
        return UnsupportedType()
    if type(json_value) not in [int, float]:
        raise JsonerException(f'Type int or float was expected, found: {type(json_value)}, value: {json_value}')
    return json_value


def encode_date(typ, value):
    if typ != date:
        return UnsupportedType()
    return value.strftime("%Y-%m-%d")


def decode_date(typ, json_value):
    if typ != date:
        return UnsupportedType()
    if not isinstance(json_value, str):
        raise JsonerException(f'date should be represented as str, found {json_value}')
    parsed_datetime = datetime.datetime.strptime(json_value, "%Y-%m-%d")
    return parsed_datetime.date()


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
    encode_date,
    encode_generic_list,
    encode_generic_dict,
    encode_union,
    encode_dataclass,
    encode_list,
    encode_dict
]

decoders = [
    decode_primitive,
    decode_float,
    decode_date,
    decode_generic_list,
    decode_generic_dict,
    decode_union,
    decode_dataclass
]


def decode(typ, json_value):
    for decoder in decoders:
        result = decoder(typ, json_value)
        if not isinstance(result, UnsupportedType):
            return result
    raise JsonerException(f'Unsupported type {typ}')


def loads(typ, json_str):
    json_value = json.loads(json_str)
    return decode(typ, json_value)


def encode(value, typ=None):
    typ = typ if typ is not None else type(value)
    for encoder in encoders:
        result = encoder(typ, value)
        if not isinstance(result, UnsupportedType):
            return result
    raise JsonerException(f'Unsupported type {typ}')


def dumps(value, typ=None, indent=None):
    json_value = encode(value, typ)
    json_str = json.dumps(json_value, indent=indent)
    return json_str

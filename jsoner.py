import json
from typing import *
import typing_inspect as inspect
import dataclasses
import datetime
from datetime import date


NoneType = type(None)


class JsonerException(Exception):
    pass


class PrimitiveSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ in [int, str, bool, NoneType]

    @staticmethod
    def encode(typ, value):
        if not type(value) == typ:
            raise JsonerException(f'Type {typ} was expected, found: {value}')
        return value

    @staticmethod
    def decode(typ, json_value):
        if not type(json_value) == typ:
            raise JsonerException(f'Type {typ} was expected, found type: {type(json_value)} value: {json_value}')
        return json_value


class FloatSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ == float

    @staticmethod
    def encode(typ, value):
        if not type(value) == typ:
            raise JsonerException(f'Type {typ} was expected, found: {value}')
        return value

    @staticmethod
    def decode(typ, json_value):
        if type(json_value) not in [int, float]:
            raise JsonerException(f'Type int or float was expected, found: {type(json_value)}, value: {json_value}')
        return json_value


class DateSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ == date

    @staticmethod
    def encode(typ, value):
        return value.strftime("%Y-%m-%d")

    @staticmethod
    def decode(typ, json_value):
        if not isinstance(json_value, str):
            raise JsonerException(f'date should be represented as str, found {json_value}')
        parsed_datetime = datetime.datetime.strptime(json_value, "%Y-%m-%d")
        return parsed_datetime.date()


class DataclassSerializer:
    @staticmethod
    def is_applicable(typ):
        return dataclasses.is_dataclass(typ)

    @staticmethod
    def encode(typ, value):
        return {field.name: encode(value.__dict__[field.name], field.type) for field in dataclasses.fields(typ)}

    @staticmethod
    def decode(typ, json_value):
        ctor_params = {field.name: decode(field.type, json_value[field.name]) for field in dataclasses.fields(typ)}
        value = typ(**ctor_params)
        return value


class ListSerializer:
    @staticmethod
    def is_applicable(typ):
        return inspect.is_generic_type(typ) and inspect.get_origin(typ) == list

    @staticmethod
    def encode(typ, value):
        item_type, = inspect.get_args(typ)
        return [encode(item, item_type) for item in value]

    @staticmethod
    def decode(typ, json_value):
        item_type = inspect.get_args(typ)[0]
        return [decode(item_type, item) for item in json_value]


class UntypedListSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ == list

    @staticmethod
    def encode(typ, value):
        return [encode(item, None) for item in value]


class UntypedDictSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ == dict

    @staticmethod
    def encode(typ, value):
        return {item_key: encode(item_value, None) for item_key, item_value in value.items()}


class DictSerializer:
    @staticmethod
    def is_applicable(typ):
        return inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict

    @staticmethod
    def encode(typ, value):
        key_type, value_type = inspect.get_args(typ)
        if key_type != str:
            raise JsonerException(f'Dict key type {key_type} is not supported for JSON serializatio, key should be of type str')
        return {key: encode(value, value_type) for (key, value) in value.items()}

    @staticmethod
    def decode(typ, json_value):
        key_type, value_type = inspect.get_args(typ)
        if key_type != str:
            raise JsonerException(f'Dict key type {key_type} is not supported for JSON deserialization - key should be str')
        return {key: decode(value_type, value) for (key, value) in json_value.items()}


class UnionSerializer:
    @staticmethod
    def is_applicable(typ):
        return inspect.is_union_type(typ)

    @staticmethod
    def encode(typ, value):
        union_types = inspect.get_args(typ)
        for union_type in union_types:
            try:
                return encode(value, union_type)
            except JsonerException:
                pass
        raise JsonerException(f'Value {value} can not be deserialized as {typ}')

    @staticmethod
    def decode(typ, json_value):
        union_types = inspect.get_args(typ)
        for union_type in union_types:
            try:
                return decode(union_type, json_value)
            except JsonerException:
                pass
        raise JsonerException(f'Value {json_value} can not be deserialized as {typ}')


serializers = [
    PrimitiveSerializer,
    FloatSerializer,
    DateSerializer,
    ListSerializer,
    DictSerializer,
    UnionSerializer,
    DataclassSerializer,
    UntypedListSerializer,
    UntypedDictSerializer
]

deserializers = [
    PrimitiveSerializer,
    FloatSerializer,
    DateSerializer,
    ListSerializer,
    DictSerializer,
    UnionSerializer,
    DataclassSerializer
]


def decode(typ, json_value):
    for deserializer in deserializers:
        if deserializer.is_applicable(typ):
            return deserializer.decode(typ, json_value)
    raise JsonerException(f'Unsupported type {typ}')


def from_json(typ, json_str):
    json_value = json.loads(json_str)
    return decode(typ, json_value)


def encode(value, typ=None):
    typ = typ if typ is not None else type(value)
    for serializer in serializers:
        if serializer.is_applicable(typ):
            return serializer.encode(typ, value)
    raise JsonerException(f'Unsupported type {typ}')


def to_json(value, typ=None):
    json_value = encode(value, typ)
    json_str = json.dumps(json_value)
    return json_str

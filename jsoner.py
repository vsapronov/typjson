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
    def serialize(obj, typ):
        if not type(obj) == typ:
            raise JsonerException(f'Type {typ} was expected, found: {obj}')
        return obj

    @staticmethod
    def deserialize(typ, data):
        if not type(data) == typ:
            raise JsonerException(f'Type {typ} was expected, found: {data}')
        return data


class FloatSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ == float

    @staticmethod
    def serialize(obj, typ):
        if not type(obj) == typ:
            raise JsonerException(f'Type {typ} was expected, found: {obj}')
        return obj

    @staticmethod
    def deserialize(typ, data):
        if type(data) not in [int, float]:
            raise JsonerException(f'Type int or float was expected, found: {type(data)}, value: {data}')
        return data


class DateSerializer:
    @staticmethod
    def is_applicable(typ):
        return typ == date

    @staticmethod
    def serialize(obj, typ):
        return obj.strftime("%Y-%m-%d")

    @staticmethod
    def deserialize(typ, json_data):
        if not isinstance(json_data, str):
            raise JsonerException(f'date should be represented as str, found {json_data}')
        parsed_datetime = datetime.datetime.strptime(json_data, "%Y-%m-%d")
        return parsed_datetime.date()


class DataclassSerializer:
    @staticmethod
    def is_applicable(typ):
        return dataclasses.is_dataclass(typ)

    @staticmethod
    def serialize(obj, typ):
        return {field.name: serialize(obj.__dict__[field.name], field.type) for field in dataclasses.fields(typ)}

    @staticmethod
    def deserialize(typ, json_data):
        ctor_params = {field.name: deserialize(field.type, json_data[field.name]) for field in dataclasses.fields(typ)}
        obj = typ(**ctor_params)
        return obj


class ListSerializer:
    @staticmethod
    def is_applicable(typ):
        return inspect.is_generic_type(typ) and inspect.get_origin(typ) == list

    @staticmethod
    def serialize(obj, typ):
        item_type, = inspect.get_args(typ)
        return [serialize(item, item_type) for item in obj]

    @staticmethod
    def deserialize(typ, json_data):
        item_type = inspect.get_args(typ)[0]
        return [deserialize(item_type, item) for item in json_data]


class DictSerializer:
    @staticmethod
    def is_applicable(typ):
        return inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict

    @staticmethod
    def serialize(obj, typ):
        key_type, value_type = inspect.get_args(typ)
        if key_type != str:
            raise JsonerException(f'Dict key type {key_type} is not supported for JSON serializatio, key should be of type str')
        return {key: serialize(value, value_type) for (key, value) in obj.items()}

    @staticmethod
    def deserialize(typ, json_data):
        key_type, value_type = inspect.get_args(typ)
        if key_type != str:
            raise JsonerException(f'Dict key type {key_type} is not supported for JSON deserialization - key should be str')
        return {key: deserialize(value_type, value) for (key, value) in json_data.items()}


class UnionSerializer:
    @staticmethod
    def is_applicable(typ):
        return inspect.is_union_type(typ)

    @staticmethod
    def serialize(obj, typ):
        union_types = inspect.get_args(typ)
        for union_type in union_types:
            try:
                return serialize(obj, union_type)
            except JsonerException:
                pass
        raise JsonerException(f'Value {obj} can not be deserialized as {typ}')

    @staticmethod
    def deserialize(typ, json_data):
        union_types = inspect.get_args(typ)
        for union_type in union_types:
            try:
                return deserialize(union_type, json_data)
            except JsonerException:
                pass
        raise JsonerException(f'Value {json_data} can not be deserialized as {typ}')


serializers = [
    PrimitiveSerializer,
    FloatSerializer,
    DateSerializer,
    ListSerializer,
    DictSerializer,
    UnionSerializer,
    DataclassSerializer
]


def deserialize(typ, json_data):
    for serializer in serializers:
        if serializer.is_applicable(typ):
            return serializer.deserialize(typ, json_data)
    raise JsonerException(f'Unsupported type {typ}')


def from_json(typ, json_str):
    json_data = json.loads(json_str)
    return deserialize(typ, json_data)


def serialize(data, typ=None):
    typ = typ if typ is not None else type(data)
    for serializer in serializers:
        if serializer.is_applicable(typ):
            return serializer.serialize(data, typ)
    raise JsonerException(f'Unsupported type {typ}')


def to_json(data, typ=None):
    json_data = serialize(data, typ)
    return json.dumps(json_data)

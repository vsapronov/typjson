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
    def is_applicable(self, typ):
        return typ == int or typ == str or typ == bool or typ == float or typ == NoneType

    def serialize(self, obj):
        return obj

    def deserialize(self, typ, data):
        if not type(data) == typ:
            raise JsonerException(f'Type {typ} was expected, found: {data}')
        return data


class DateSerializer:
    def is_applicable(self, typ):
        return typ == date

    def serialize(self, obj):
        return obj.strftime("%Y-%m-%d")

    def deserialize(self, typ, data):
        if not isinstance(data, str):
            raise JsonerException(f'date should be represented as str, found {data}')
        parsed_datetime = datetime.datetime.strptime(data, "%Y-%m-%d")
        return parsed_datetime.date()


class DataclassSerializer:
    def is_applicable(self, typ):
        return dataclasses.is_dataclass(typ)

    def serialize(self, obj):
        return obj.__dict__

    def deserialize(self, typ, data):
        ctor_params = {}
        for field_name, field_typ in fields(typ).items():
            item_value = data[field_name]
            field_value = convert(field_typ, item_value)
            ctor_params[field_name] = field_value
        obj = typ(**ctor_params)
        return obj


class ListSerializer:
    def is_applicable(self, typ):
        return inspect.is_generic_type(typ) and inspect.get_origin(typ) == list

    def serialize(self, obj):
        return obj

    def deserialize(self, typ, data):
        item_type = inspect.get_args(typ)[0]
        return [convert(item_type, item) for item in data]


class DictSerializer:
    def is_applicable(self, typ):
        return inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict

    def serialize(self, obj):
        return obj

    def deserialize(self, typ, data):
        key_type, value_type = inspect.get_args(typ)
        if key_type != str:
            raise JsonerException(f'Dict key type {key_type} is not supported for JSON deserialization - key should be str')
        return {key: convert(value_type, value) for (key, value) in data.items()}


class UnionSerializer:
    def is_applicable(self, typ):
        return inspect.is_union_type(typ)

    def serialize(self, obj):
        return obj

    def deserialize(self, typ, data):
        union_types = inspect.get_args(typ)
        for union_type in union_types:
            try:
                return convert(union_type, data)
            except JsonerException:
                pass
        raise JsonerException(f'Value {data} can not be deserialized as {typ}')


serializers = [
    PrimitiveSerializer(),
    DateSerializer(),
    ListSerializer(),
    DictSerializer(),
    UnionSerializer(),
    DataclassSerializer()
]


class JsonerEncoder(json.JSONEncoder):
    def default(self, o):
        typ = type(o)
        for serializer in serializers:
            if serializer.is_applicable(typ):
                return serializer.serialize(o)
        raise JsonerException(f'Unsupported type {typ}')


def fields(typ):
    return typ.__annotations__ if hasattr(typ, '__annotations__') else None


def convert(typ, data):
    for serializer in serializers:
        if serializer.is_applicable(typ):
            return serializer.deserialize(typ, data)
    raise JsonerException(f'Unsupported type {typ}')


def from_json(typ, obj):
    data = json.loads(obj)
    return convert(typ, data)


def to_json(obj):
    return json.dumps(obj, cls=JsonerEncoder)

import json
from typing import *
from typing_inspect import *


class JsonerException(Exception):
    pass


class JsonerEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
# if type(o) == date:
#     return str(o)
#   else:


def to_json(obj):
    return json.dumps(obj, cls=JsonerEncoder)


def fields(typ):
    return typ.__annotations__ if hasattr(typ, '__annotations__') else None


def convert(typ, data):
    if is_optional_type(typ):
        return data
    if is_generic_type(typ):
        return data
    if typ == int or typ == str:
        return data
    else:
        ctor_params = {}
        for field_name, field_typ in fields(typ).items():
            item_value = data[field_name]
            field_value = convert(field_typ, item_value)
            ctor_params[field_name] = field_value
        obj = typ(**ctor_params)
        return obj


def from_json(typ, obj):
    data = json.loads(obj)
    return convert(typ, data)

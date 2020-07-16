from typjson.encoding import *
import json

T = TypeVar('T')


def loads(typ: Type[T], json_str: str) -> T:
    json_value = json.loads(json_str, parse_float=Decimal)
    return decode(typ, json_value)


def dumps(value: T, typ: Optional[Type[T]] = None, indent: int = None) -> str:
    json_value = encode(value, typ)
    json_str = json.dumps(json_value, indent=indent)
    return json_str

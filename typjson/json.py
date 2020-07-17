from typjson.encoding import *
import json

T = TypeVar('T')


json_encoders = [
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
]

json_decoders = [
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


json_weak_encoders = [
    encode_list,
    encode_dict
]


def loads(
        typ: Type[T],
        json_str: str,
        ) -> T:
    json_value = json.loads(json_str, parse_float=Decimal)
    return decode(typ, json_value, decoders=json_decoders)


def dumps(
        value: T,
        typ: Optional[Type[T]] = None,
        allow_weak_types=True,
        indent: int = None,
        ) -> str:
    if not allow_weak_types and typ is None:
        raise UnsupportedType('type is not provided and allow_weak_types is set to False')
    all_encoders = json_encoders
    if allow_weak_types:
        all_encoders += json_weak_encoders
    json_value = encode(value, typ, encoders=all_encoders)
    json_str = json.dumps(json_value, indent=indent)
    return json_str

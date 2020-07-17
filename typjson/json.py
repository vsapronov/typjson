from typjson.encoding import *
import json


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


M = TypeVar('M')
K = TypeVar('K')


EncodeFunc = Callable[[Decoder, Type[K], K], Any]
DecodeFunc = Callable[[Decoder, Type[K], Any], K]


def loads(
        typ: Type[M],
        json_str: str,
        decoders: List[DecodeFunc] = [],
        ) -> M:
    json_value = json.loads(json_str, parse_float=Decimal)
    return decode(typ, json_value, decoders=decoders+json_decoders)


def dumps(
        value: M,
        typ: Optional[Type[M]] = None,
        allow_weak_types: bool = True,
        encoders: List[EncodeFunc] = [],
        indent: int = None,
        ) -> str:
    if not allow_weak_types and typ is None:
        raise JsonerException('type is not provided and allow_weak_types is set to False')
    all_encoders = encoders+json_encoders
    if allow_weak_types:
        all_encoders += json_weak_encoders
    json_value = encode(value, typ, encoders=all_encoders)
    json_str = json.dumps(json_value, indent=indent)
    return json_str

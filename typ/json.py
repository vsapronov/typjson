from typing import IO
from typ.encoding import *
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
    encode_generic_tuple,
    encode_generic_set,
    encode_union,
    encode_dataclass,
    encode_any,
    encode_list,
    encode_dict,
    encode_tuple,
    encode_set,
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
    decode_generic_tuple,
    decode_generic_set,
    decode_union,
    decode_dataclass,
    decode_any,
]

M = TypeVar('M')
K = TypeVar('K')

EncodeFunc = Callable[[Decoder, Type[K], K], Union[Any, UnsupportedType]]
DecodeFunc = Callable[[Decoder, Type[K], Any], Union[K, UnsupportedType]]


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
        encoders: List[EncodeFunc] = [],
        indent: Optional[int] = None,
        ) -> str:
    json_value = encode(value, typ, encoders=encoders+json_encoders)
    return json.dumps(json_value, indent=indent)


def load(
        fp: IO[str],
        typ: Type[M],
        decoders: List[DecodeFunc] = [],
        ) -> M:
    json_value = json.load(fp, parse_float=Decimal)
    return decode(typ, json_value, decoders=decoders+json_decoders)


def dump(
        fp: IO[str],
        value: M,
        typ: Optional[Type[M]] = None,
        encoders: List[EncodeFunc] = [],
        indent: Optional[int] = None,
        ):
    json_value = encode(value, typ, encoders=encoders+json_encoders)
    return json.dump(json_value, fp, indent=indent)

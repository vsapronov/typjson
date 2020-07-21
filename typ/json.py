from typing import *
from typing import IO
from typ.encoding import DecodeFunc, EncodeFunc, decode, encode, json_encoders, json_decoders, JsonError
import decimal
import json


T = TypeVar('T')


def loads(
        typ: Type[T],
        json_str: str,
        decoders: List[DecodeFunc] = [],
        ) -> T:
    json_value = json.loads(json_str, parse_float=decimal.Decimal)
    return decode(typ, json_value, decoders=decoders+json_decoders)


def dumps(
        value: T,
        typ: Optional[Type[T]] = None,
        encoders: List[EncodeFunc] = [],
        indent: Optional[int] = None,
        ) -> str:
    json_value = encode(value, typ, encoders=encoders+json_encoders)
    return json.dumps(json_value, indent=indent)


def load(
        fp: IO[str],
        typ: Type[T],
        decoders: List[DecodeFunc] = [],
        ) -> T:
    json_value = json.load(fp, parse_float=decimal.Decimal)
    return decode(typ, json_value, decoders=decoders+json_decoders)


def dump(
        fp: IO[str],
        value: T,
        typ: Optional[Type[T]] = None,
        encoders: List[EncodeFunc] = [],
        indent: Optional[int] = None,
        ) -> None:
    json_value = encode(value, typ, encoders=encoders+json_encoders)
    return json.dump(json_value, fp, indent=indent)

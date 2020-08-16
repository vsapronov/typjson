from typing import TypeVar, Type, List, Optional, IO
from typ.encoding import CaseConverter, DecodeFunc, EncodeFunc, decode, encode, json_encoders, json_decoders, JsonError
import decimal
import json


T = TypeVar('T')


def loads(
        typ: Type[T],
        json_str: str,
        case: CaseConverter = None,
        decoders: List[DecodeFunc] = [],
        ) -> T:
    json_value = json.loads(json_str, parse_float=decimal.Decimal)
    return decode(typ, json_value, case=case, decoders=decoders+json_decoders)


def dumps(
        value: T,
        typ: Optional[Type[T]] = None,
        case: CaseConverter = None,
        encoders: List[EncodeFunc] = [],
        indent: Optional[int] = None,
        ) -> str:
    json_value = encode(value, typ, case=case, encoders=encoders+json_encoders)
    return json.dumps(json_value, indent=indent)


def load(
        fp: IO[str],
        typ: Type[T],
        case: CaseConverter = None,
        decoders: List[DecodeFunc] = [],
        ) -> T:
    json_value = json.load(fp, parse_float=decimal.Decimal)
    return decode(typ, json_value, case=case, decoders=decoders+json_decoders)


def dump(
        fp: IO[str],
        value: T,
        typ: Optional[Type[T]] = None,
        case: CaseConverter = None,
        encoders: List[EncodeFunc] = [],
        indent: Optional[int] = None,
        ) -> None:
    json_value = encode(value, typ, case=case, encoders=encoders+json_encoders)
    return json.dump(json_value, fp, indent=indent)

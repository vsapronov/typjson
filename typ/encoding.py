from typing import Type, TypeVar, Callable, Optional, List, Union, Any
from inspect import isclass
import typing_inspect as inspect  # type: ignore
import dataclasses
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from typ.types import char, NoneType, union
from enum import Enum
from stringcase import snakecase


class UnsupportedType:
    pass


Unsupported = UnsupportedType()

K = TypeVar('K')


EncodeFunc = Callable[['Encoder', Type[K], K], Union[Any, UnsupportedType]]
DecodeFunc = Callable[['Decoder', Type[K], Any], Union[K, UnsupportedType]]
CaseConverter = Callable[[str], str]

class JsonError(Exception):
    pass


def check_type(expected_type: Union[Type, List[Type]], value: Any):
    actual_type = type(value)
    if type(expected_type) == list:
        if not type(value) in expected_type:
            raise JsonError(f'One of types {expected_type} expected, found type: {actual_type} value: {value}')
    else:
        if type(value) != expected_type:
            raise JsonError(f'Type {expected_type} expected, found type: {actual_type} value: {value}')


def encode_primitive(encoder, typ, value):
    if typ not in [int, float, str, bool, NoneType]:
        return Unsupported
    check_type(typ, value)
    return value


def decode_primitive(decoder, typ, json_value):
    if typ not in [int, Decimal, str, bool, NoneType]:
        return Unsupported
    check_type(typ, json_value)
    return json_value


def encode_char(encoder, typ, value):
    if typ != char:
        return Unsupported
    check_type(typ, value)
    return str(value)


def decode_char(decoder, typ, json_value):
    if typ != char:
        return Unsupported
    check_type(str, json_value)
    if len(json_value) != 1:
        raise JsonError(f'char should be represented with str length 1, found: {json_value}')
    return json_value


def decode_float(decoder, typ, json_value):
    if typ != float:
        return Unsupported
    check_type([int, float, Decimal], json_value)
    return float(json_value)


def encode_decimal(encoder, typ, value):
    if typ != Decimal:
        return Unsupported
    check_type(typ, value)
    return float(value)


def encode_date(encoder, typ, value):
    if typ != date:
        return Unsupported
    check_type(typ, value)
    return value.isoformat()


def decode_date(decoder, typ, json_value):
    if typ != date:
        return Unsupported
    check_type(str, json_value)
    parsed_datetime = datetime.strptime(json_value, "%Y-%m-%d")
    return parsed_datetime.date()


def encode_datetime(encoder, typ, value):
    if typ != datetime:
        return Unsupported
    check_type(typ, value)
    return value.isoformat()


def decode_datetime(decoder, typ, json_value):
    if typ != datetime:
        return Unsupported
    check_type(str, json_value)
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"]:
        try:
            parsed = datetime.strptime(json_value, fmt)
            return parsed
        except:
            pass
    raise JsonError(f"no suitable datetime format found for {json_value}")


def encode_time(encoder, typ, value):
    if typ != time:
        return Unsupported
    check_type(typ, value)
    return value.isoformat()


def decode_time(decoder, typ, json_value):
    if typ != time:
        return Unsupported
    check_type(str, json_value)
    parsed_datetime = datetime.strptime(json_value, "%H:%M:%S")
    return parsed_datetime.time()


def encode_uuid(encoder, typ, value):
    if typ != UUID:
        return Unsupported
    check_type(typ, value)
    return str(value)


def decode_uuid(decoder, typ, json_value):
    if typ != UUID:
        return Unsupported
    check_type(str, json_value)
    return UUID(json_value)


def encode_dataclass(encoder, typ, value):
    if not dataclasses.is_dataclass(typ):
        return Unsupported
    check_type(typ, value)
    fields = dataclasses.fields(typ)
    return {encoder.to_json_case(field.name): encoder.encode(value.__dict__[field.name], field.type) for field in fields}


def decode_dataclass(decoder, typ, json_value):
    if not dataclasses.is_dataclass(typ):
        return Unsupported
    check_type(dict, json_value)
    fields = dataclasses.fields(typ)
    ctor_params = {field.name: decoder.decode(field.type, json_value.get(decoder.to_json_case(field.name))) for field in fields}
    value = typ(**ctor_params)
    return value


def encode_enum(encoder, typ, value):
    if not (isclass(typ) and issubclass(typ, Enum)):
        return Unsupported
    check_type(typ, value)
    return encoder.encode(value.value)


def decode_enum(decoder, typ, json_value):
    if not (isclass(typ) and issubclass(typ, Enum)):
        return Unsupported
    enum_member = None
    for member in list(typ):
        try:
            json_value_decoded = decoder.decode(type(member.value), json_value)
            if member.value == json_value_decoded:
                enum_member = member
                break
        except:
            pass
    if enum_member is None:
        raise JsonError(f'Failed to decode enum type {typ} from JSON value: {json_value}')
    return enum_member


def encode_generic_list(encoder, typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == list):
        return Unsupported
    check_type(list, value)
    item_type, = inspect.get_args(typ)
    return [encoder.encode(item, item_type) for item in value]


def decode_generic_list(decoder, typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == list):
        return Unsupported
    check_type(list, json_value)
    item_type = inspect.get_args(typ)[0]
    return [decoder.decode(item_type, item) for item in json_value]


def encode_generic_dict(encoder, typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict):
        return Unsupported
    check_type(dict, value)
    key_type, value_type = inspect.get_args(typ)
    if key_type != str:
        raise JsonError(f'Dict key type {key_type} is not supported for JSON serialization, key should be of type str')
    return {key: encoder.encode(value, value_type) for (key, value) in value.items()}


def decode_generic_dict(decoder, typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == dict):
        return Unsupported
    check_type(dict, json_value)
    key_type, value_type = inspect.get_args(typ)
    if key_type != str:
        raise JsonError(f'Dict key type {key_type} is not supported for JSON deserialization - key should be str')
    return {key: decoder.decode(value_type, value) for (key, value) in json_value.items()}


def encode_generic_tuple(encoder, typ, value):
    if not inspect.is_tuple_type(typ):
        return Unsupported
    check_type(tuple, value)
    items_types = inspect.get_args(typ)
    if len(items_types) != len(value):
        raise JsonError(f'Expected tuple of size: {len(items_types)}, found tuple of size: {len(value)}, value: {value}')
    return tuple(map(lambda item, item_type: encoder.encode(item, item_type), value, items_types))


def decode_generic_tuple(decoder, typ, json_value):
    if not inspect.is_tuple_type(typ):
        return Unsupported
    check_type(list, json_value)
    items_types = inspect.get_args(typ)
    if len(items_types) != len(json_value):
        raise JsonError(f'Expected list of size: {len(items_types)}, found tuple of size: {len(json_value)}, value: {json_value}')
    return tuple(map(lambda item, item_type: decoder.decode(item_type, item), json_value, items_types))


def encode_generic_set(encoder, typ, value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == set):
        return Unsupported
    check_type(set, value)
    item_type, = inspect.get_args(typ)
    return [encoder.encode(item, item_type) for item in value]


def decode_generic_set(decoder, typ, json_value):
    if not (inspect.is_generic_type(typ) and inspect.get_origin(typ) == set):
        return Unsupported
    check_type(list, json_value)
    item_type = inspect.get_args(typ)[0]
    return set([decoder.decode(item_type, item) for item in json_value])


def encode_union(encoder, typ, value):
    if not inspect.is_union_type(typ):
        return Unsupported
    union_types = inspect.get_args(typ)
    for union_type in union_types:
        try:
            return encoder.encode(value, union_type)
        except JsonError:
            pass
    raise JsonError(f'Value {value} can not be deserialized as {typ}')


def decode_union(decoder, typ, json_value):
    if not inspect.is_union_type(typ):
        return Unsupported
    union_types = inspect.get_args(typ)
    for union_type in union_types:
        try:
            return decoder.decode(union_type, json_value)
        except JsonError:
            pass
    raise JsonError(f'Value {json_value} can not be deserialized as {typ}')


def encode_tagged_union(encoder, typ, value):
    if not union.isunion(typ):
        return Unsupported
    json_value_key = encoder.to_json_case(union.member_name(value))
    json_value_val = encoder.encode(value.value, union.member_type(value))
    return {json_value_key: json_value_val}


def decode_tagged_union(decoder, typ, json_value):
    if not union.isunion(typ):
        return Unsupported
    check_type(dict, json_value)
    if len(json_value) != 1:
        raise JsonError(f'Value {json_value} can not be deserialized as {typ} tagged_union should be represented as object with single field')
    json_value_key = list(json_value.keys())[0]
    json_value_val = json_value[json_value_key]
    member = next((m for m in union.members(typ) if decoder.to_json_case(m) == json_value_key), None)
    member_type = union.members(typ)[member]
    if member_type is None:
        return union.create_member(typ, member, None)
    else:
        return union.create_member(typ, member, decoder.decode(member_type, json_value_val))


def encode_any(encoder, typ, value):
    if typ != Any:
        return Unsupported
    return encoder.encode(value, typ=type(value))


def decode_any(decoder, typ, json_value):
    if typ != Any:
        return Unsupported
    return decoder.decode(type(json_value), json_value)


def encode_list(encoder, typ, value):
    if typ != list:
        return Unsupported
    check_type(list, value)
    return [encoder.encode(item, typ=None) for item in value]


def encode_dict(encoder, typ, value):
    if typ != dict:
        return Unsupported
    check_type(dict, value)
    return {item_key: encoder.encode(item_value, typ=None) for item_key, item_value in value.items()}


def encode_tuple(encoder, typ, value):
    if typ != tuple:
        return Unsupported
    check_type(tuple, value)
    return [encoder.encode(item, typ=None) for item in value]


def encode_set(encoder, typ, value):
    if typ != set:
        return Unsupported
    check_type(set, value)
    return [encoder.encode(item, typ=None) for item in value]


T = TypeVar('T')


class Decoder:
    def __init__(self, decoders, to_json_case):
        self.decoders = decoders
        self._to_json_case = to_json_case

    def to_json_case(self, name):
        if self._to_json_case is None:
            return name
        return self._to_json_case(name)

    def decode(self, typ: Type[T], json_value: Any) -> T:
        for decoder in self.decoders:
            result = decoder(self, typ, json_value)
            if result != Unsupported:
                return result
        raise JsonError(f'Unsupported type {typ}')


class Encoder:
    def __init__(self, encoders, to_json_case):
        self.encoders = encoders
        self._to_json_case = to_json_case

    def to_json_case(self, name):
        if self._to_json_case is None:
            return name
        return self._to_json_case(name)

    def encode(self, value: T, typ: Optional[Type[T]] = None):
        typ = typ if typ is not None else type(value)
        for encoder in self.encoders:
            result = encoder(self, typ, value)
            if result != Unsupported:
                return result
        raise JsonError(f'Unsupported type {typ}')


def decode(typ: Type[T], json_value: Any, case: CaseConverter = None, decoders: List[DecodeFunc] = []):
    try:
        return Decoder(decoders, case).decode(typ, json_value)
    except Exception as error:
        if error is JsonError:
            raise error
        raise JsonError(f'Error during decoding: {error}')


def encode(value: T, typ: Optional[Type[T]] = None, case: CaseConverter = None, encoders: List[EncodeFunc] = []):
    try:
        return Encoder(encoders, case).encode(value, typ)
    except Exception as error:
        if error is JsonError:
            raise error
        raise JsonError(f'Error during encoding: {error}')

json_encoders: List[EncodeFunc] = [
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
    encode_enum,
    encode_tagged_union,
    encode_any,
    encode_list,
    encode_dict,
    encode_tuple,
    encode_set,
]

json_decoders: List[DecodeFunc] = [
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
    decode_enum,
    decode_tagged_union,
    decode_any,
]

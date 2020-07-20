# typjson

Type-safe JSON (de)serialization for Python. Compatible with mypy type hints.

## Requirements

* Python 3.7 or newer

## Features

* Support for primitive types:
    * `str`, `int`, `float`, `bool`, `Decimal`, `None`
    * `date` as `"%Y-%m-%d"`, `datetime` as `"%Y-%m-%dT%H:%M:%S%z"`, `time` as `"%H:%M:%S"`
    * `UUID` as `str` in format `"8-4-4-4-12"`
    * `char` type as `str` of length 1 
* Support for `Union[]` and therefore `Optional[]` type
* Structure types: `List[]`, `Tuple[]`, `Dict[str, T]`, `Set[]`
* Support for [data classes](https://docs.python.org/3/library/dataclasses.html)
* Support for custom encoders and decoders

## Simple Usage

```python
from typ import json
from typing import *
from datetime import date
from dataclasses import dataclass


@dataclass
class Address:
    street: str
    house: int
    apt: Optional[str]


@dataclass
class Person:
    first_name: str
    last_name: str
    languages: List[str]
    address: Address
    birth_date: date


person = Person(
    "John",
    "Smith",
    ["English", "Russian"],
    Address("Main", 1, "2A"),
    date(year=1984, month=8, day=1)
)

json_str = json.dumps(person, indent=2)
loaded_person = json.loads(Person, json_str)

assert person == loaded_person
```

Value of `json_str` that is dumped and loaded in the code example above looks like:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "languages": [
    "English",
    "Russian"
  ],
  "address": {
    "street": "Main",
    "house": 1,
    "apt": "2A"
  },
  "birth_date": "1984-08-01"
}
```

## API Overview

typjson API is similar to [json](https://docs.python.org/3/library/json.html) module. Main functions are defined in `typ.json` module. In fact `typ.json` functions are using `json` module under the hood for final conversion of python structures into JSON.

### typ.json.dumps

`typ.json.dumps(value: M, typ: Optional[Type[M]] = None, encoders: List[EncodeFunc] = [], indent: Optional[int] = None) -> str`

Serialize value to a JSON formatted str using specified type.

`value` Python object to be serialized to JSON.

`typ` type information for `value`. If `None` is provided then actual type of `value` is used otherwise `value` is checked to be valid instance of `typ`.

`encoders` list of custom encoders, see [custom encoding](#custom-encoding).

`indent` optional non-negative indent level for JSON. If `None` is provided then JSON is represented as single line without indentation.

Returns JSON string or raises `JsonError`.

### typ.json.dump

`typ.json.dump(fp: IO[str], value: M, typ: Optional[Type[M]] = None, encoders: List[EncodeFunc] = [], indent: Optional[int] = None)`

Serialize value as a JSON formatted stream.

`fp` stream to write JSON to.

Other arguments have the same meaning as in [typ.json.dumps](#typjsondumps).

### typ.json.loads

`typ.json.loads(typ: Type[M], json_str: str, decoders: List[DecodeFunc] = []) -> M`

Deserialize json_str to a Python object of specified type.

`typ` type to deserialize JSON into.

`json_str` string containing JSON.

`decoders` list of custom decoders, see [custom encoding](#custom-encoding).

Returns instance of `M` or raises `JsonError`.

### typ.json.load

`typ.json.load(fp: IO[str], typ: Type[M], decoders: List[DecodeFunc] = []) -> M`

Deserialize stream to a Python object of specified type.

`fp` stream to read JSON from.

Other arguments have the same meaning as in [typ.json.loads](#typjsonloads)

## Supported Types

### Primitive Types

| Python type                          | JSON type | Notes                                             |
| :----------------------------------- | :-------- | :------------------------------------------------ |
| int                                  | number    |                                                   |
| float                                | number    |                                                   |
| decimal.Decimal                      | number    |                                                   |
| boolean                              | boolean   |                                                   |
| typ.typing.char                      | string    | string with length 1                              |
| str                                  | string    |                                                   |
| uuid                                 | string    | lower case hex symbols with hyphens as 8-4-4-4-12 |
| datetime.date                        | string    | ISO 8601 yyyy-mm-dd                               |
| datetime.datetime                    | string    | ISO 8601 yyyy-mm-ddThh:mm:ss.ffffff               |
| datetime.time                        | string    | ISO 8601 hh:mm:ss.ffffff                          |
| typ.typing.NoneType <br/> type(None) | null      |                                                   |
| Any                                  | any type  | represents nothing, similar to unit is some langs |

### Structure Types

| Python type           | JSON type     | Notes                                                             |
| :-------------------- | :------------ | ----------------------------------------------------------------- |
| List[T]               | array         | homogeneous, items of T                                           |
| Dict[str, T]          | object        | with field names corresponding to dictionary keys and values of T |
| Set[T]                | array         | homogeneous, items of T                                           |
| Tuple[T, ...]         | array         | homogeneous, items of T                                           |
| Union[T, K]           | either T or K |                                                                   |
| list                  | array         | heterogeneous                                                     |
| dict                  | object        |                                                                   |
| tuple                 | array         | heterogeneous                                                     |
| dataclasses.dataclass | object        | field types are respected                                         |

### Null-safety

All types can not have `None` value besides `NoneType` aka `type(None)`. `Optional[T]` allows `None` value. So if nullable `str` is needed `Optional[str]` would be a good fit.
`Optional[T]` type is in fact `Union[T, NoneType]` therefore in typjson it's supported via `Union[]` support. Because of this `Optional[T]` is not listed above since it's just a `Union`.

## Custom Encoding

# typjson

Type-safe JSON (de)serialization for Python. Compatible with mypy type hints.

## Requirements

* Python 3.7 or newer

## Features

* Type safety in runtime and mypy compatibility
* Support for types out of the box:
  * Primitive types:
      * `str`, `int`, `float`, `bool`, `Decimal`, `None`
      * `date` as `"%Y-%m-%d"`, `datetime` as `"%Y-%m-%dT%H:%M:%S%z"`, `time` as `"%H:%M:%S"`
      * `UUID` as `str` in format `"8-4-4-4-12"`
      * `char` type as `str` of length 1
  * `Union[]` and therefore `Optional[]`
  * Structure types: `List[]`, `Tuple[]`, `Dict[str, T]`, `Set[]`
  * [Enum classes](https://docs.python.org/3/library/enum.html)
  * [Data classes](https://docs.python.org/3/library/dataclasses.html)
* Support for custom encoders and decoders
* API similar to standard [json module](https://docs.python.org/3/library/json.html)

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

## Type Safety

### Runtime

What is type safety in Python? Since Python is dynamically typed language it's hard to provide any types guarantees before runtime. However types could be checked in run time. This is exactly what typjson library is doing.
Consider following example for `Address` type defined above:
```python
from typ import json
from typing import *
from dataclasses import dataclass


@dataclass
class Address:
    street: str
    house: int
    apt: Optional[str]

json_str = """{"street": "Main", "house": 1, "apt": 2}"""
loaded_address = json.loads(Address, json_str)
```

The `apt` field has type defined as `Optional[str]` however value provided in JSON is `2` which is `number` type in JSON and it's obviously not compatible with `Optional[str]`.
Respectively `json.loads` call will raise `JsonError`:
```
typ.encoding.JsonError: Value 2 can not be deserialized as typing.Union[str, NoneType]
```
Call `json.loads` will either return instance of requested type with all nested types checked or raise a error. This is runtime type safety of typjson.

### Compile Time (mypy)

Functions in `typ.json` module `dumps`, `loads`, `dump`, `load` have proper type hints. Therefore types could be validated with [mypy](http://mypy-lang.org/) tool:
```python
json_str = """{"street": "Main", "house": 1, "apt": 2}"""
loaded_address = json.loads(Address, json_str)
loaded_address = "some other address"
```
This will produce error in mypy as type of `loaded_address` is inferred as `Address`:
```
error: Incompatible types in assignment (expression has type "str", variable has type "Address")
```
This provides type safety in compile time.

## API Overview

typjson API is similar to [json](https://docs.python.org/3/library/json.html) module API. Main functions are defined in `typ.json` module. Most useful functions are [`typ.json.loads`](#typjsonloads) and [`typ.json.dumps`](#typjsondumps). If something went wrong during JSON encoding/decoding then [`JsonError`](#typjsonjsonerror) is raised.
In fact `typ.json` functions are using `json` module under the hood for final conversion between python structures and JSON.

List of supported types if provided [here](#supported-types).
[Custom Encoding](#custom-encoding) section describes how any type could be supported in addition to types that are supported out of the box.

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
| uuid.UUID                            | string    | lower case hex symbols with hyphens as 8-4-4-4-12 |
| datetime.date                        | string    | ISO 8601 yyyy-mm-dd                               |
| datetime.datetime                    | string    | ISO 8601 yyyy-mm-ddThh:mm:ss.ffffff               |
| datetime.time                        | string    | ISO 8601 hh:mm:ss.ffffff                          |
| typ.typing.NoneType <br/> type(None) | null      |                                                   |

### Non Primitive Types

| Python type                         | JSON type            | Notes                                             |
| :-----------------------------------| :------------------- | ------------------------------------------------- |
| List[T]                             | array                | homogeneous, items encoded                        |
| Dict[str, T]                        | object               | fields values of T encoded                        |
| Set[T]                              | array                | homogeneous, items of T encoded                   |
| Tuple[T, K, ...]                    | array                | heterogeneous, items of T, K, ... encoded         |
| Union[T, K, ...]                    | look for T, K, ...   | T, K, ... encoded                                 |
| list                                | array                | heterogeneous, items are encoded                  |
| dict                                | object               |                                                   |
| tuple                               | array                | heterogeneous, items are encoded                  |
| Enum classes                        | look for member type | enum members are encoded according to their types |
| class decorated with<br/>@dataclass | object               | field types are respected                         |
| class decorated with<br/>@union     | object               | object with single field                          |
| Any                                 | any type             | anything                                          |


### Null-safety

All types can not have `None` value besides `NoneType` aka `type(None)`. `Optional[T]` allows `None` value.
So if nullable `str` is needed `Optional[str]` would be a good fit.
`Optional[T]` type is in fact `Union[T, NoneType]` therefore in typjson it's supported via `Union[]` support.
Because of this `Optional[T]` is not listed above since it's just a `Union`.

## Custom Encoding

In fact all types that are supported out of the box are supported via encoders and decoders. Examples of custom encoder and decoder are provided just for basic understanding. For deeper insight the one might be interested to look at source code of `typ.encoding` module.

### Custom Encoder

[typ.json.dump](#typjsondump) and [typ.json.dumps](#typjsondumps) functions take list of encoders as a parameter.
Those encoders are custom encoders that are used in addition to standard built-in encoders.
Let's implement custom encoder that will code all integers as strings in JSON:
```python
from typ.encoding import Unsupported, check_type

def encode_int_custom(encoder, typ, value):
    if typ != int:
        # if this encoder is not applicable to the typ it should return Unsupported
        return Unsupported
    # there's a helper function checking that value is instance of specified type - int
    check_type(int, value)
    # return encoded value
    return str(value)

from typ import json
assert json.dumps([3, 4, 5], encoders=[encode_int_custom]) == '["3", "4", "5"]'
```

In the code above `encode_int_custom` is provided into `typ.json.dumps` call and it's used prior standard built-in `int` encoding. As it's deemostrated in the assert it successfully encoded integers as strings. Please never do this in real life - this code is provided only for demonstration purposes.

Encoder function is defined as: `Callable[['Encoder', Type[K], K], Union[Any, UnsupportedType]]`
There's an `encoder` parameter of every custom encoder which holds instance of [Encoder](#typencodingencoder). It is useful for encoding nested types, like lists or classes, etc.

### Custom Decoder

[typ.json.load](#typjsonload) and [typ.json.loads](#typjsonloads) functions take list of decoders as a parameter.
Similarly to [encoding](#custom-encoder) it's useful for custom decoding logic.
Here's a mirror example for decoding `int` type from strings in JSON:
```python
from typ.encoding import Unsupported, check_type

def decode_int_custom(decoder, typ, json_value):
    if typ != int:
        # if this encoder is not applicable to the typ it should return Unsupported
        return Unsupported
    # check that JSON has string in the json_value
    check_type(str, json_value)
    # return decoded value
    return int(json_value)

from typ import json
assert loads(List[int], '["3", "4", "5"]', decoders=[decode_int_custom]) == [3, 4, 5]
```

Decoder function is defined as: `Callable[['Decoder', Type[K], Any], Union[K, UnsupportedType]]`.

## API Reference

### typ.json.dumps

`typ.json.dumps(value: T, typ: Optional[Type[T]] = None, case: CaseConverter = None, encoders: List[EncodeFunc] = [], indent: Optional[int] = None) -> str`

Serialize value to a JSON formatted str using specified type.

`value` Python object to be serialized to JSON.

`typ` type information for `value`.
If `None` is provided then actual type of `value` is used otherwise `value` is checked to be valid instance of `typ`.

`case` case converter, see [fields case](#fields-case).

`encoders` list of custom encoders, see [custom encoding](#custom-encoding).

`indent` optional non-negative indent level for JSON. If `None` is provided then JSON is represented as single line without indentation.

Returns JSON string or raises `JsonError`.

### typ.json.dump

`typ.json.dump(fp: IO[str], value: T, typ: Optional[Type[T]] = None, case: CaseConverter = None, encoders: List[EncodeFunc] = [], indent: Optional[int] = None) -> None`

Serialize value as a JSON formatted stream.

`fp` stream to write JSON to.

Other arguments have the same meaning as in [typ.json.dumps](#typjsondumps).

### typ.json.loads

`typ.json.loads(typ: Type[T], json_str: str, case: CaseConverter = None, decoders: List[DecodeFunc] = []) -> T`

Deserialize json_str to a Python object of specified type.

`typ` type to deserialize JSON into.

`json_str` string containing JSON.

`case` case converter, see [fields case](#fields-case).

`decoders` list of custom decoders, see [custom encoding](#custom-encoding).

Returns instance of `M` or raises `JsonError`.

### typ.json.load

`typ.json.load(fp: IO[str], typ: Type[T], case: CaseConverter = None, decoders: List[DecodeFunc] = []) -> T`

Deserialize stream to a Python object of specified type.

`fp` stream to read JSON from.

Other arguments have the same meaning as in [typ.json.loads](#typjsonloads)

### typ.json.JsonError (defined as typ.encoding.JsonError)

`JsonError` raised in case of any issue during encoding/decoding JSON data according to type information provided.

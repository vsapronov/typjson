# typjson

Type-safe JSON (de)serialization for Python. Compatible with mypy type hints.

## Requirements

* Python 3.7 or newer

## Features

* Support for primitive types:
    * `str`, `int`, `float`, `Decimal`, `bool`
    * `date` as `"%Y-%m-%d"`, `datetime` as `"%Y-%m-%dT%H:%M:%S%z"`, `time` as `"%H:%M:%S"`
    * `UUID` as `str` in format `"8-4-4-4-12"`
* Support for None type and Optional type
* Support for Union[] generic type
* Structure types: List[], Tuple[], Dict[str, T]
* Support for classes marked with `@dataclass`
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
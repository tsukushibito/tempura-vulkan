import dataclasses
from typing import List


@dataclasses.dataclass
class BaseType:
    name: str
    typedef: str


@dataclasses.dataclass
class BitMask:
    name: str
    typedef: str


@dataclasses.dataclass
class Handle:
    name: str


@dataclasses.dataclass
class Param:
    type_: str
    name: str


@dataclasses.dataclass
class FuncPointer:
    name: str
    return_type: str
    params: List[Param]


@dataclasses.dataclass
class Enum:
    name: str
    value: int


@dataclasses.dataclass
class Enums:
    name: str
    enums: List[Enum]


@dataclasses.dataclass
class Member:
    name: str
    type_: str


@dataclasses.dataclass
class Struct:
    name: str
    members: List[Member]


@dataclasses.dataclass
class Union:
    name: str
    members: List[Member]


@dataclasses.dataclass
class Command:
    name: str
    return_type: str
    params: List[Param]

import dataclasses
from dataclasses import dataclass, field
from typing import List


def c_type_to_rs_type(c_type: str):

    table = {'void': 'c_void',
             'char': 'i8',
             'float': 'f32',
             'double': 'f64',
             'uint8_t': 'u8',
             'uint16_t': 'u16',
             'uint32_t': 'u32',
             'uint64_t': 'u64',
             'int32_t': 'i32',
             'int64_t': 'i64',
             'size_t': 'size_t',
             'int': 'i32', }

    return table.get(c_type, c_type)


@dataclass
class BaseType:
    name: str
    typedef: str

    def to_rs(self):
        return ('type ' + self.name
                + ' = '
                + c_type_to_rs_type(self.typedef) + ';\n')


@dataclass
class BitMask:
    name: str
    typedef: str

    def to_rs(self):
        return ('type ' + self.name
                + ' = '
                + c_type_to_rs_type(self.typedef) + ';\n')


@dataclass
class Handle:
    name: str

    def to_rs(self):
        return ('enum ' + self.name + '_t { }\n'
                + 'type ' + self.name + ' = *mut ' + self.name + ';\n')


@dataclass
class Param:
    type_: str
    name: str


@dataclass
class FuncPointer:
    name: str
    return_type: str
    params: List[Param]

    def to_rs(self):
        rs = ('type ' + self.name + ' = ' +
              '::std::option::Option<extern "C" fn(')
        rs_params = map(lambda p: p.name + ': ' + p.type_, self.params)
        rs += ', '.join(rs_params)
        rs += ');\n'

        return rs


@dataclass
class Enum:
    name: str
    value: int


@dataclass
class Enums:
    name: str
    enums: List[Enum]

    def to_rs(self):
        rs = ('struct ' + self.name + '(u32);')
        for e in self.enums:
            rs += e.name + ': ' + self.name + ' = ' + e.value + ';\n'

        return rs


@dataclass
class Member:
    name: str
    type_: str


@dataclass
class Struct:
    name: str
    members: List[Member]

    def to_rs(self):
        rs = '#[repr(C)]'
        rs += ('struct ' + self.name + ' {\n')
        for m in self.members:
            rs += '    ' + m.name + ': ' + c_type_to_rs_type(m.type_) + ',\n'
        rs += '}\n'
        return rs


@dataclass
class Union:
    name: str
    members: List[Member]

    def to_rs(self):
        rs = '#[repr(C)]'
        rs += ('union ' + self.name + ' {\n')
        for m in self.members:
            rs += '    ' + m.name + ': ' + c_type_to_rs_type(m.type_) + ',\n'
        rs += '}\n'
        return rs


@dataclass
class Command:
    name: str
    return_type: str
    params: List[Param]

    def to_rs(self):
        rs = ('extern "C" fn(')
        rs_params = map(lambda p: p.name + ': ' + p.type_, self.params)
        rs += ', '.join(rs_params)
        rs += ');\n'

        return rs


@dataclass
class Elements:
    basetypes: List[BaseType] = field(default_factory=list)
    bitmasks: List[BitMask] = field(default_factory=list)
    handles: List[Handle] = field(default_factory=list)
    functionpointers: List[FuncPointer] = field(default_factory=list)
    enums: List[Enums] = field(default_factory=list)
    structs: List[Struct] = field(default_factory=list)
    unions: List[Union] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)

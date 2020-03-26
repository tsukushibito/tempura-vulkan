import dataclasses
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

    return table.get(c_type, 'unknown')


@dataclasses.dataclass
class BaseType:
    name: str
    typedef: str

    def to_rs(self):
        return ('type ' + self.name
                + ' = '
                + c_type_to_rs_type(self.typedef) + ';\n')


@dataclasses.dataclass
class BitMask:
    name: str
    typedef: str

    def to_rs(self):
        return ('type ' + self.name
                + ' = '
                + c_type_to_rs_type(self.typedef) + ';\n')


@dataclasses.dataclass
class Handle:
    name: str

    def to_rs(self):
        return ('enum ' + self.name + '_t { }\n'
                + 'type ' + self.name + ' = *mut ' + self.name + ';\n')


@dataclasses.dataclass
class Param:
    type_: str
    name: str


@dataclasses.dataclass
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


@dataclasses.dataclass
class Enum:
    name: str
    value: int


@dataclasses.dataclass
class Enums:
    name: str
    enums: List[Enum]

    def to_rs(self):
        rs = ('struct ' + self.name + '(u32);')
        for e in self.enums:
            rs += e.name + ': ' + self.name + ' = ' + e.value + ';\n'

        return rs


@dataclasses.dataclass
class Member:
    name: str
    type_: str


@dataclasses.dataclass
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


@dataclasses.dataclass
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


@dataclasses.dataclass
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

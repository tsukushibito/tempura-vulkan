import sys
import os
import argparse
import re
from dataclasses import dataclass

from clang.cindex import Index, Config, TranslationUnit

is_including_other_file = False
source_file_path = ''


def dump(node, file, indent=0):
    kind = node.kind.name
    name = node.spelling
    typ = node.type.get_canonical().spelling
    f = os.path.basename(node.extent.start.file.name)

    should_dump = kind != 'TYPE_REF' and kind != 'TYPEDEF_DECL'
    # should_dump = True
    if not is_including_other_file:
        if f != os.path.basename(source_file_path):
            should_dump = False

    if should_dump:
        line = '\t' * indent + '[' + kind + '] name: ' + \
            name + ', type: ' + typ
        if kind == 'ENUM_CONSTANT_DECL':
            line += ', value: ' + str(node.enum_value)
        # print(line)
        file.write(line + '\n')

        for child in node.get_children():
            dump(child, file, indent+1)


class Converted:
    enums: list = list()
    unions: list = list()
    structs: list = list()
    functions: list = list()

    def __init__(
            self,
            enums: list = list(),
            unions: list = list(),
            structs: list = list(),
            functions: list = list()):
        self.enums = enums
        self.unions = unions
        self.structs = structs
        self.functions = functions


def convert(node, converted):
    kind = node.kind.name
    if kind == 'ENUM_DECL':
        converted.enums.append(convert_enum(node))
        return converted
    elif kind == 'STRUCT_DECL':
        converted.structs.append(convert_struct(node))
        return converted
    elif kind == 'UNION_DECL':
        converted.unions.append(convert_union(node))
        return converted
    elif kind == 'FUNCTION_DECL':
        converted.functions.append(convert_function(node))
        return converted
    elif kind == 'TYPEDEF_DECL':
        return converted
    else:
        for child in node.get_children():
            converted = convert(child, converted)
        return converted


def convert_enum(node):
    if node.kind.name != 'ENUM_DECL':
        return ''

    enum_name = node.spelling
    rust_enum = '#[repr(C)]\n'
    rust_enum += 'enum ' + enum_name + ' {\n'
    for child in node.get_children():
        if(child.kind.name != 'ENUM_CONSTANT_DECL'):
            continue
        constant_name = child.spelling
        constant_value = child.enum_value
        rust_enum += '    ' + constant_name + \
            ' = ' + str(constant_value) + ',\n'

    rust_enum += '}\n'

    rust_enum += '\n'
    return rust_enum


def convert_struct(node):
    if node.kind.name != 'STRUCT_DECL':
        return ''

    struct_name = node.spelling
    if any(True for _ in node.get_children()):
        rust_struct = '#[repr(C)]\n'
        rust_struct += 'struct ' + struct_name + ' {\n'
        for child in node.get_children():
            if child.kind.name == 'FIELD_DECL':
                field_name = child.spelling
                field_type = child.type.get_canonical().spelling
                rust_struct += '    ' + field_name + \
                    ': ' + convert_primitive_type(field_type) + ',\n'
        rust_struct += '}\n'
    else:
        rust_struct = 'enum ' + struct_name + ' {}\n'

    rust_struct += '\n'
    return rust_struct


def convert_union(node):
    if node.kind.name != 'UNION_DECL':
        return ''

    union_name = node.spelling
    if any(True for _ in node.get_children()):
        rust_union = '#[repr(C)]\n'
        rust_union += 'union ' + union_name + ' {\n'
        for child in node.get_children():
            if child.kind.name == 'FIELD_DECL':
                field_name = child.spelling
                field_type = child.type.get_canonical().spelling
                rust_union += '    ' + field_name + \
                    ': ' + convert_primitive_type(field_type) + ',\n'
        rust_union += '}\n'
    else:
        rust_union = 'enum ' + union_name + ' {}\n'

    rust_union += '\n'
    return rust_union


def convert_function(node):
    if node.kind.name != 'FUNCTION_DECL':
        return ''
    func_name = node.spelling
    return_type = convert_primitive_type(
        node.result_type.get_canonical().spelling)

    if any(True for _ in node.get_children()):
        rust_func = 'fn ' + func_name + '(\n'
        is_first_param = True
        for child in node.get_children():
            if child.kind.name == 'PARM_DECL':
                param_name = child.spelling
                param_type = convert_primitive_type(
                    child.type.get_canonical().spelling)
                if not is_first_param:
                    rust_func += ',\n'
                rust_func += '    ' + param_name + ': ' + param_type
                is_first_param = False

        if return_type == 'c_void':
            rust_func += ');\n'
        else:
            rust_func += ') -> ' + return_type + ';\n'

    else:
        rust_func = 'fn ' + func_name + '()'
        if return_type == 'c_void':
            rust_func += ';\n'
        else:
            rust_func += ' -> ' + return_type + ';\n'
    rust_func += '\n'
    return rust_func


def convert_primitive_type(c_type):
    pattern = re.compile(r'(^const )')
    match = pattern.search(c_type)
    if match:
        is_const = True
        c_type = c_type[match.end():]
    else:
        is_const = False

    pattern = re.compile(r'(\*$)')
    match = pattern.search(c_type)
    if match:
        is_pointer = True
        c_type = c_type[0:match.start() - 1:]
    else:
        is_pointer = False

    pattern = re.compile(r'(^struct )|(^enum )|(^union )')
    match = pattern.search(c_type)
    if match:
        c_type = c_type[match.end():]

    pattern = re.compile(r'\[\d+\]')
    match = pattern.search(c_type)
    if match:
        is_array = True
        s = match.start() + 1
        e = match.end() - 1
        array_length = c_type[s:e]
        t = c_type[0: match.start() - 1]
    else:
        is_array = False
        t = c_type

    mapping = {
        'bool': 'bool',
        'char': 'c_char',
        'double': 'c_double',
        'float': 'c_float',
        'int': 'c_int',
        'signed int': 'c_int',
        'long': 'c_long',
        'signed long': 'c_long',
        'long long': 'c_longlong',
        'signed long long': 'c_longlong',
        'short': 'c_short',
        'signed short': 'c_short',
        'unsigned char': 'c_uchar',
        'unsigned int': 'c_uint',
        'unsigned long': 'c_ulong',
        'unsigned long long': 'c_ulonglong',
        'unsigned short': 'c_short',
        'void': 'c_void',
    }

    if t in mapping:
        if is_array:
            rs_type = '[' + mapping[t] + '; ' + array_length + ']'
        else:
            rs_type = mapping[t]
    else:
        rs_type = t

    if is_pointer:
        if is_const:
            rs_type = '*const ' + rs_type
        else:
            rs_type = '*mut ' + rs_type

    return rs_type


def main():
    global is_including_other_file
    global source_file_path

    parser = argparse.ArgumentParser(
        description='Convert C++ header file to rust source file.')

    parser.add_argument('src', help='C++ header file path.')
    parser.add_argument('dst', help='Output file path.')
    parser.add_argument('--CLANG_LIBRARY_PATH', help='Clang library path.')
    parser.add_argument('-i', '--include', action='store_true',
                        help='Include included file')

    args = parser.parse_args()

    print('src='+args.src)
    print('dst='+args.dst)
    print('CLANG_LIBRARY_PATH='+str(args.CLANG_LIBRARY_PATH))
    print('include='+str(args.include))

    source_file_path = args.src
    is_including_other_file = args.include

    if args.CLANG_LIBRARY_PATH:
        Config.set_library_path(args.CLANG_LIBRARY_PATH)
    else:
        CLANG_LIBRARY_PATH = 'CLANG_LIBRARY_PATH'
        if CLANG_LIBRARY_PATH in os.environ:
            clang_library_path = os.environ[CLANG_LIBRARY_PATH]
            Config.set_library_path(clang_library_path)

    index = Index.create()

    tu = index.parse(args.src,
                     options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    file_test = open(args.dst+'.txt', 'w')
    dump(tu.cursor, file_test)
    file_test.close()

    converted = convert(tu.cursor, Converted())
    file = open(args.dst, 'w')
    file.writelines(converted.enums)
    file.writelines(converted.unions)
    file.writelines(converted.structs)
    file.writelines(converted.functions)
    file.close()


if __name__ == '__main__':
    main()

import sys
import os
import argparse
import clang.cindex
from clang.cindex import Index, Config, TranslationUnit
import re

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


def traverse(node, converter):
    if converter(node):
        for child in node.get_children():
            traverse(child, converter)


def convert(node, converted):
    kind = node.kind.name
    if kind == 'ENUM_DECL':
        return converted + convert_enum(node)
    elif kind == 'ENUM_DECL':
        return converted + convert_struct(node)
    else:
        for child in node.get_children():
            converted = convert(child, converted)


def convert_enum(node):
    if node.kind.name != 'ENUM_DECL':
        return ''

    enum_name = node.spelling
    rust_enum = 'enum ' + enum_name + ' {\n'
    for child in node.get_children():
        if(child.kind.name != 'ENUM_CONSTANT_DECL'):
            continue
        constant_name = child.spelling
        constant_value = child.enum_value
        rust_enum += '    ' + constant_name + \
            ' = ' + str(constant_value) + ',\n'

    rust_enum += '}\n'

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
                    ': ' + c_type_to_rs_type(field_type) + ',\n'
        rust_struct += '}\n'
    else:
        rust_struct = 'enum ' + struct_name + ' {}\n'

    return rust_struct


def c_type_to_rs_type(c_type):
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

    pattern = re.compile(r'(^struct )|(^enum )')
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

    file = open(args.dst, 'w')
    dump(tu.cursor, file)
    file.close()


if __name__ == '__main__':
    main()

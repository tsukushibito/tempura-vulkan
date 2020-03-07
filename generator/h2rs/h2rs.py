import sys
import os
import argparse
import clang.cindex
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
        rust_struct = 'struct ' + struct_name + ' {\n'
        rust_struct += '}\n'
    else:
        rust_struct = 'enum ' + struct_name + ' {}\n'

    return rust_struct


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

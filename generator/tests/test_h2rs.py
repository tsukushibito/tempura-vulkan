import unittest
import os
from clang.cindex import Index, Config, TranslationUnit
from h2rs.h2rs import convert_enum, convert_struct


class TestConverter(unittest.TestCase):

    def test_convert_enum(self):
        temp_file = 'temp.h'
        file = open(temp_file, 'w')
        file.write(
            'typedef enum Foo {\n'
            '    ONE=1,\n'
            '    TWO=2,\n'
            '    THREE=ONE + TWO,\n'
            '    FOUR=THREE + 1,\n'
            '    MAX=0x7FFFFFFF\n'
            '} Foo;\n'
        )
        file.close()

        if Config.library_path == None:
            clang_library_path = os.environ['CLANG_LIBRARY_PATH']
            Config.set_library_path(clang_library_path)

        index = Index.create()
        tu = index.parse(temp_file,
                         options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

        children = tu.cursor.get_children()
        rust_enum = convert_enum(next(children))

        expected = (
            'enum Foo {\n'
            '    ONE = 1,\n'
            '    TWO = 2,\n'
            '    THREE = 3,\n'
            '    FOUR = 4,\n'
            '    MAX = 2147483647,\n'
            '}\n')
        print(rust_enum)
        print(expected)
        self.assertEqual(rust_enum, expected)

        os.remove(temp_file)

    def test_convert_struct_opaque(self):
        temp_file = 'temp.h'
        file = open(temp_file, 'w')
        file.write(
            'struct Foo;'
        )
        file.close()

        if Config.library_path == None:
            clang_library_path = os.environ['CLANG_LIBRARY_PATH']
            Config.set_library_path(clang_library_path)

        index = Index.create()
        tu = index.parse(temp_file,
                         options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

        children = tu.cursor.get_children()
        rust_struct = convert_struct(next(children))

        expected = 'enum Foo {}\n'
        print(rust_struct)
        print(expected)
        self.assertEqual(rust_struct, expected)

        os.remove(temp_file)

    def test_convert_struct(self):
        temp_file = 'temp.h'
        file = open(temp_file, 'w')
        file.write(
            'struct Bar;\n'
            'union Baz;\n'
            'struct Foo {\n'
            '    int value;\n'
            '    int array_value[4];\n'
            '    Bar struct_value;\n'
            '    Bar * struct_ptr;\n'
            '    const Bar * const_struct_ptr;\n'
            '    void * void_ptr;\n'
            '    const void * const_void_ptr;\n'
            '    const char * str;\n'
            '    Baz union_value;\n'
            '};\n'
        )
        file.close()

        if Config.library_path == None:
            clang_library_path = os.environ['CLANG_LIBRARY_PATH']
            Config.set_library_path(clang_library_path)

        index = Index.create()
        tu = index.parse(temp_file,
                         options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

        children = tu.cursor.get_children()
        next(children)
        next(children)
        rust_struct = convert_struct(next(children))

        expected = (
            '#[repr(C)]\n'
            'struct Foo {\n'
            '    value: c_int,\n'
            '    array_value: [c_int; 4],\n'
            '    struct_value: Bar,\n'
            '    struct_ptr: *mut Bar,\n'
            '    const_struct_ptr: *const Bar,\n'
            '    void_ptr: *mut c_void,\n'
            '    const_void_ptr: *const c_void,\n'
            '    str: *const c_char,\n'
            '    union_value: Baz,\n'
            '}\n'
        )
        print(rust_struct)
        print(expected)
        self.assertEqual(rust_struct, expected)

        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()

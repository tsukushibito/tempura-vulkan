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
            'struct Foo {\n'
            '    int value;\n'
            '    int array_value[4];\n'
            '    Bar struct_value;\n'
            '}\n'
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

        expected = (
            'struct Foo {\n'
            '    value: i32,\n'
            '    array_value: [i32; 4],\n'
            '    struct_value: Bar,\n'
            '}\n'
        )
        print(rust_struct)
        print(expected)
        self.assertEqual(rust_struct, expected)

        os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()

import sys
import os
import clang.cindex
from clang.cindex import Index, Config, TranslationUnit


def dump(cursor, file, indent=0):
    kind = cursor.kind.name
    name = cursor.spelling
    typ = cursor.type.get_canonical().spelling
    line = '\t' * indent + '[' + kind + '] name: ' + name + ', type: ' + typ
    print(line)
    file.write(line + '\n')

    for child in cursor.get_children():
        dump(child, file, indent+1)


def main():
    CLANG_LIBRARY_PATH = 'CLANG_LIBRARY_PATH'
    VULKAN_SDK = 'VULKAN_SDK'

    if CLANG_LIBRARY_PATH in os.environ:
        clang_library_path = os.environ[CLANG_LIBRARY_PATH]
        Config.set_library_path(clang_library_path)

    index = Index.create()
    vulkan_sdk_path = os.environ[VULKAN_SDK]

    vulkan_header = vulkan_sdk_path + '/include/vulkan/vulkan.h'
    tu = index.parse(vulkan_header,
                     options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)

    file = open('vulkan.rs.txt', 'w')
    dump(tu.cursor, file)
    file.close()


if __name__ == '__main__':
    main()

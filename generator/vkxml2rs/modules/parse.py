import xml.etree.ElementTree as ET

from .elements import *


def parse_vk_xml(xml_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    elements = Elements()
    for child in root:
        if child.tag == 'types':
            parse_types(child, elements)


def parse_basetype(node: ET.Element):
    typedef = node[0].text
    name = node[1].text
    return BaseType(name, typedef)


def parse_bitmask(node: ET.Element):
    typedef = node[0].text
    name = node[1].text
    return BitMask(name, typedef)


def parse_handle(node: ET.Element):
    name = node[1].text
    return Handle(name)


def parse_funcpointer(node: ET.Element):
    name = node[0].text
    return_type = node.text.split()[1]
    name_tail = node[0].tail.split()
    is_const = False
    is_pointer = False
    if len(name_tail) > 0 and name_tail[-1] == 'const':
        is_const = True

    params = []
    for e in node.iter('type'):
        param_type = e.text
        tails = e.tail.split()
        param_name = tails[-1]
        if tails[0] == '*':
            is_pointer = True

        if is_pointer:
            if is_const:
                param_type = 'const ' + param_type + ' *'
            else:
                param_type = param_type * ' *'
        param = Param(param_type, param_name)
        params.append(param)

    return FuncPointer(name, return_type, params)


def parse_struct(node: ET.Element):
    struct = Struct()


def parse_types(node: ET.Element, elements: Elements):
    for child in node:
        if child.tag != 'type':
            continue

        category = child.attrib.get('category')
        if category == 'basetype':
            basetype = parse_basetype(child)
            elements.basetypes.append(basetype)

        elif category == 'bitmask':
            bitmask = parse_bitmask(child)
            elements.bitmasks.append(bitmask)

        elif category == 'handle':
            handle = parse_handle(child)
            elements.handles.append(handle)

        elif category == 'funcpointer':
            funcpointer = parse_funcpointer(child)
            elements.functionpointers.append(funcpointer)

    return elements


def parse_enums():
    pass

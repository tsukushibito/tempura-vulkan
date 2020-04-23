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
        if e.get('category') == 'funcpointer':
            continue
        param_type = e.text
        tails = e.tail.split()
        if tails[0] == '*':
            is_pointer = True
            param_name = tails[1]
        else:
            is_pointer = False
            param_name = tails[0]
        param_name = param_name.replace(',', '')
        param_name = param_name.replace(')', '')
        param_name = param_name.replace(';', '')

        if is_pointer:
            if is_const:
                param_type = 'const ' + param_type + ' *'
            else:
                param_type = param_type + ' *'
        param = Param(param_type, param_name)
        params.append(param)
        is_const = tails[-1] == 'const'

    return FuncPointer(name, return_type, params)


def parse_enums(node: ET.Element):
    name = node.attrib['name']
    if not node.attrib.get('type'):
        return None

    enum_type = node.attrib['type']
    enums = []
    for child in node.getchildren():
        enum_name = child.attrib['name']
        if child.attrib.get('alias'):
            alias_name = child.attrib['alias']
            aliases = list(filter(lambda x: x.name == alias_name, enums))
            assert len(aliases) > 0
            enum_value = aliases[0].value
        else:
            if enum_type == 'enum':
                enum_value = int(child.attrib['value'])
            elif enum_type == 'bitmask':
                enum_value = 1 << int(child.attrib['bitpos'])
            else:
                assert False, 'Unknown type.'
        enums.append(Enum(enum_name, enum_value))

    return Enums(name, enums)


def parse_struct(node: ET.Element):
    name = node.attrib['name']
    members = []
    for child in node.getchildren():
        if child.tag != 'member':
            continue

        is_const = False
        if child.text is not None:
            words = child.text.split()
            is_const = len(words) > 0 and words[0] == 'const'

        member_type = child[0].text

        is_pointer = False
        if child[0].tail is not None:
            words = child[0].tail.split()
            is_pointer = len(words) > 0 and words[0] == '*'

        member_name = child[1].text

        if is_pointer:
            if is_const:
                member_type = 'const ' + member_type + ' *'
            else:
                member_type = member_type + ' *'

        member = Member(member_name, member_type)
        members.append(member)

    return Struct(name, members)


def parse_types(node: ET.Element, elements: Elements):
    for child in node:
        if child.tag != 'type':
            continue

        category = child.attrib.get('category')
        if category == 'basetype':
            basetype = parse_basetype(child)
            elements.basetypes.append(basetype)

        elif category == 'handle':
            handle = parse_handle(child)
            elements.handles.append(handle)

        elif category == 'funcpointer':
            funcpointer = parse_funcpointer(child)
            elements.functionpointers.append(funcpointer)

    return elements

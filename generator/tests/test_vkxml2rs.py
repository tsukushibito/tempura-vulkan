import unittest
import os
import pprint
import dataclasses

import xml.etree.ElementTree as ET
# from vkxml2rs.elements import *
# from vkxml2rs.parse import *
from vkxml2rs import *
from modules.parse import *


class TestConverter(unittest.TestCase):
    def test_parse_basetype(self):
        xml = (
            '<types>'
            '    <type category="basetype">typedef <type>uint32_t</type> <name>VkSampleMask</name>;</type>'
            '    <type category="basetype">typedef <type>uint32_t</type> <name>VkBool32</name>;</type>'
            '    <type category="basetype">typedef <type>uint32_t</type> <name>VkFlags</name>;</type>'
            '    <type category="basetype">typedef <type>uint64_t</type> <name>VkDeviceSize</name>;</type>'
            '    <type category="basetype">typedef <type>uint64_t</type> <name>VkDeviceAddress</name>;</type>'
            '</types>'
        )
        root = ET.fromstring(xml)
        children = root.getchildren()
        basetypes = []
        for child in children:
            basetypes.append(parse_basetype(child))

        self.assertEqual(basetypes[0], BaseType('VkSampleMask', 'uint32_t'))
        self.assertEqual(basetypes[1], BaseType('VkBool32', 'uint32_t'))
        self.assertEqual(basetypes[2], BaseType('VkFlags', 'uint32_t'))
        self.assertEqual(basetypes[3], BaseType('VkDeviceSize', 'uint64_t'))
        self.assertEqual(basetypes[4], BaseType('VkDeviceAddress', 'uint64_t'))


if __name__ == '__main__':
    unittest.main()

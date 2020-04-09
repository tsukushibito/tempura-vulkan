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

    def test_parse_bitmask(self):
        xml = (
            '<types>'
            '    <type requires="VkFramebufferCreateFlagBits" category="bitmask">typedef <type>VkFlags</type> <name>VkFramebufferCreateFlags</name>;</type>'
            '    <type category="bitmask">typedef <type>VkFlags</type> <name>VkQueryPoolCreateFlags</name>;</type>'
            '</types>'
        )
        root = ET.fromstring(xml)
        children = root.getchildren()
        bitmasks = []
        for child in children:
            bitmasks.append(parse_bitmask(child))

        self.assertEqual(bitmasks[0], BitMask(
            'VkFramebufferCreateFlags', 'VkFlags'))
        self.assertEqual(bitmasks[1], BitMask(
            'VkQueryPoolCreateFlags', 'VkFlags'))

    def test_parse_handle(self):
        xml = (
            '<types>'
            '    <type category="handle"><type>VK_DEFINE_HANDLE</type>(<name>VkInstance</name>)</type>'
            '    <type category="handle" parent="VkInstance"><type>VK_DEFINE_HANDLE</type>(<name>VkPhysicalDevice</name>)</type>'
            '</types>'
        )
        root = ET.fromstring(xml)
        children = root.getchildren()
        handles = []
        for child in children:
            handles.append(parse_handle(child))

        self.assertEqual(handles[0], Handle('VkInstance'))
        self.assertEqual(handles[1], Handle('VkPhysicalDevice'))

    def test_parse_funcpointer(self):
        xml = (
            '<types>'
            '    <type category="funcpointer">typedef VkBool32 (VKAPI_PTR *<name>PFN_vkDebugReportCallbackEXT</name>)('
            '    <type>VkDebugReportFlagsEXT</type>                       flags,'
            '    <type>VkDebugReportObjectTypeEXT</type>                  objectType,'
            '    <type>uint64_t</type>                                    object,'
            '    <type>size_t</type>                                      location,'
            '    <type>int32_t</type>                                     messageCode,'
            '    const <type>char</type>*                                 pLayerPrefix,'
            '    const <type>char</type>*                                 pMessage,'
            '    <type>void</type>*                                       pUserData);</type>'
            '</types>'
        )
        root = ET.fromstring(xml)
        children = root.getchildren()
        funcpointers = []
        for child in children:
            funcpointers.append(parse_funcpointer(child))

        self.assertEqual(
            funcpointers[0],
            FuncPointer(
                'PFN_vkDebugReportCallbackEXT',
                'VkBool32',
                [
                    Param('VkDebugReportFlagsEXT', 'flags'),
                    Param('VkDebugReportObjectTypeEXT', 'objectType'),
                    Param('uint64_t', 'object'),
                    Param('size_t', 'location'),
                    Param('int32_t', 'messageCode'),
                    Param('const char *', 'pLayerPrefix'),
                    Param('const char *', 'pMessage'),
                    Param('void *', 'pUserData'),
                ]))
        # print(funcpointers[0])
        # expected = FuncPointer(
        #     'PFN_vkDebugReportCallbackEXT',
        #     'VkBool32',
        #     [
        #         Param('VkDebugReportFlagsEXT', 'flags'),
        #         Param('VkDebugReportObjectTypeEXT', 'objectType'),
        #         Param('uint64_t', 'object'),
        #         Param('size_t', 'location'),
        #         Param('int32_t', 'messageCode'),
        #         Param('const char *', 'pLayerPrefix'),
        #         Param('const char *', 'pMessage'),
        #         Param('void *', 'pUserData'),
        #     ])
        # print(expected)


if __name__ == '__main__':
    unittest.main()

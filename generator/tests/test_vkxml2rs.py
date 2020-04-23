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
            '<types>\n'
            '<type category="funcpointer">typedef VkBool32 (VKAPI_PTR *<name>PFN_vkDebugReportCallbackEXT</name>)(\n'
            '<type>VkDebugReportFlagsEXT</type>                       flags,\n'
            '<type>VkDebugReportObjectTypeEXT</type>                  objectType,\n'
            '<type>uint64_t</type>                                    object,\n'
            '<type>size_t</type>                                      location,\n'
            '<type>int32_t</type>                                     messageCode,\n'
            'const <type>char</type>*                                 pLayerPrefix,\n'
            'const <type>char</type>*                                 pMessage,\n'
            '<type>void</type>*                                       pUserData);</type>\n'
            '<type category="funcpointer" requires="VkDebugUtilsMessengerCallbackDataEXT">typedef VkBool32 (VKAPI_PTR *<name>PFN_vkDebugUtilsMessengerCallbackEXT</name>)(\n'
            '<type>VkDebugUtilsMessageSeverityFlagBitsEXT</type>           messageSeverity,\n'
            '<type>VkDebugUtilsMessageTypeFlagsEXT</type>                  messageTypes,\n'
            'const <type>VkDebugUtilsMessengerCallbackDataEXT</type>*      pCallbackData,\n'
            '<type>void</type>*                                            pUserData);</type>\n'
            '</types>\n'
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
        self.assertEqual(
            funcpointers[1],
            FuncPointer(
                'PFN_vkDebugUtilsMessengerCallbackEXT',
                'VkBool32',
                [
                    Param('VkDebugUtilsMessageSeverityFlagBitsEXT',
                          'messageSeverity'),
                    Param('VkDebugUtilsMessageTypeFlagsEXT', 'messageTypes'),
                    Param('const VkDebugUtilsMessengerCallbackDataEXT *',
                          'pCallbackData'),
                    Param('void *', 'pUserData'),
                ]))

    def test_parse_enums(self):
        xml = (
            '<registry>'
            '    <enums name="VkPerformanceCounterScopeKHR" type="enum">\n'
            '        <enum value="0"     name="VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_BUFFER_KHR"/>\n'
            '        <enum value="1"     name="VK_PERFORMANCE_COUNTER_SCOPE_RENDER_PASS_KHR"/>\n'
            '        <enum value="2"     name="VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_KHR"/>\n'
            '        <enum               name="VK_QUERY_SCOPE_COMMAND_BUFFER_KHR" alias="VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_BUFFER_KHR"/>\n'
            '        <enum               name="VK_QUERY_SCOPE_RENDER_PASS_KHR" alias="VK_PERFORMANCE_COUNTER_SCOPE_RENDER_PASS_KHR"/>\n'
            '        <enum               name="VK_QUERY_SCOPE_COMMAND_KHR" alias="VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_KHR"/>\n'
            '    </enums>\n'
            '    <comment>Flags</comment>\n'
            '    <enums name="VkQueueFlagBits" type="bitmask">\n'
            '        <enum bitpos="0"    name="VK_QUEUE_GRAPHICS_BIT"                             comment="Queue supports graphics operations"/>\n'
            '        <enum bitpos="1"    name="VK_QUEUE_COMPUTE_BIT"                              comment="Queue supports compute operations"/>\n'
            '        <enum bitpos="2"    name="VK_QUEUE_TRANSFER_BIT"                             comment="Queue supports transfer operations"/>\n'
            '        <enum bitpos="3"    name="VK_QUEUE_SPARSE_BINDING_BIT"                       comment="Queue supports sparse resource memory management operations"/>\n'
            '    </enums>\n'
            '</registry>\n'
        )
        root = ET.fromstring(xml)
        children = root.getchildren()
        enums = []
        for child in children:
            if child.tag == 'enums':
                enums.append(parse_enums(child))

        self.assertEqual(enums[0], Enums('VkPerformanceCounterScopeKHR', [
            Enum('VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_BUFFER_KHR', 0),
            Enum('VK_PERFORMANCE_COUNTER_SCOPE_RENDER_PASS_KHR', 1),
            Enum('VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_KHR', 2),
            Enum('VK_QUERY_SCOPE_COMMAND_BUFFER_KHR', 0),
            Enum('VK_QUERY_SCOPE_RENDER_PASS_KHR', 1),
            Enum('VK_QUERY_SCOPE_COMMAND_KHR', 2),
        ]))
        self.assertEqual(enums[1], Enums('VkQueueFlagBits', [
            Enum('VK_QUEUE_GRAPHICS_BIT', 1),
            Enum('VK_QUEUE_COMPUTE_BIT', 2),
            Enum('VK_QUEUE_TRANSFER_BIT', 4),
            Enum('VK_QUEUE_SPARSE_BINDING_BIT', 8),
        ]))

    def test_parse_struct(self):
        xml = (
            '<registry>'
            '    <type category="struct" name="VkApplicationInfo">\n'
            '        <member values="VK_STRUCTURE_TYPE_APPLICATION_INFO"><type>VkStructureType</type> <name>sType</name></member>\n'
            '        <member>const <type>void</type>*     <name>pNext</name></member>\n'
            '        <member optional="true" len="null-terminated">const <type>char</type>*     <name>pApplicationName</name></member>\n'
            '        <member><type>uint32_t</type>        <name>applicationVersion</name></member>\n'
            '        <member optional="true" len="null-terminated">const <type>char</type>*     <name>pEngineName</name></member>\n'
            '        <member><type>uint32_t</type>        <name>engineVersion</name></member>\n'
            '        <member><type>uint32_t</type>        <name>apiVersion</name></member>\n'
            '    </type>\n'
            '</registry>\n'
        )
        root = ET.fromstring(xml)
        children = root.getchildren()
        structs = []
        for child in children:
            if child.tag == 'type' and child.attrib['category'] == 'struct':
                structs.append(parse_struct(child))

        self.assertEqual(structs[0], Struct('VkApplicationInfo', [
            Member('sType', 'VkStructureType'),
            Member('pNext', 'const void *'),
            Member('pApplicationName', 'const char *'),
            Member('applicationVersion', 'uint32_t'),
            Member('pEngineName', 'const char *'),
            Member('engineVersion', 'uint32_t'),
            Member('apiVersion', 'uint32_t'),
        ]))


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

#===- cindex-dump.py - cindex/Python Source Dump -------------*- python -*--===#
#
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
#===------------------------------------------------------------------------===#

"""
A tool for converting c++-interfaces into a c-based version
"""

import sys
from pathlib import Path
import clang.cindex
from clang.cindex import Config
from optparse import OptionParser

script_path = Path(sys.argv[0]).parent
Config.set_library_path("{}/build/venv/Lib/site-packages/clang/native".format(script_path))

#C:\Projekt3\toolchain_c_interface\build\_deps\pluginterfaces-src\base

def parsing(tu, method_count, struct_count, interface_count, method_args, method_args_content):

    tu_spelling = []
    tu_location = []
    tu_kind = []
    tu_access_specifier = []

    interface_open_bracket = 0
    struct_open_bracket = 0
    enum_open_bracket = 0
    within_interface = 0
    within_method = 0
    this_method_count = 0
    within_brackets = 0
    within_enum = 0
    within_struct = 0
    within_struct_part = 0
    j = 0

    method_args_content_string = ""

    for i in tu.get_tokens(extent=tu.cursor.extent):

        tu_spelling.append(i.spelling)
        tu_location.append(i.location)
        tu_kind.append(i.kind)
        tu_access_specifier.append(i.cursor.access_specifier)


    for i in tu.get_tokens(extent=tu.cursor.extent):

        # ----- Interfaces ------------------------------------------------------------------

        if tu_spelling[j - 1] != ">" and tu_spelling[j] == "class" and within_interface == 0 and\
                ((tu_spelling[j + 2] == ":" and tu_spelling[j + 3] == "public") or tu_spelling[j + 1] == "FUnknown")\
                and i.cursor.kind == i.cursor.kind.CLASS_DECL and within_interface == 0 \
                    and (tu_access_specifier[j] == i.cursor.access_specifier.PUBLIC or tu_access_specifier[j + 3] == i.cursor.access_specifier.PUBLIC):
            interface_count = interface_count + 1
            within_interface = 1

            source_file_interface.append(i.cursor.translation_unit.spelling)
            interface_name.append(tu_spelling[j + 1])
            interface_location.append(tu_location[j])
            interface_token_location.append(j)
            interface_description.append(i.cursor.brief_comment)

            method_name.append(interface_count)
            method_name[interface_count - 1] = []

            method_return.append(interface_count)
            method_return[interface_count - 1] = []

            inherits_table.append(interface_count)
            inherits_table[interface_count - 1] = []

            method_args.append(interface_count)
            method_args[interface_count - 1] = []
            ID_table.append(i.cursor.brief_comment)
            ID_table[interface_count - 1] = []



        elif tu_spelling[j] == "public" and tu_spelling[j + 1] != ":" and within_interface == 1:
            for k in range(len(inherits_table[interface_count - 1]) + 1):
                if tu_spelling[j + 1] in interface_name:
                    inherits_location = interface_name.index(tu_spelling[j + 1])
                    for n in range(len(inherits_table[inherits_location])):
                        inherits_table[interface_count - 1].append(inherits_table[inherits_location][n])
            inherits_table[interface_count - 1].append(tu_spelling[j + 1])

        elif tu_spelling[j] == "{" and within_interface == 1:
            interface_open_bracket = interface_open_bracket + 1

        elif tu_spelling[j] == "virtual" and (tu_spelling[j + 2] == "PLUGIN_API" or tu_spelling[j + 2] == "*") and within_interface == 1 and within_method == 0:
            within_method = 1
            method_count = method_count + 1
            this_method_count = this_method_count + 1

            method_args[interface_count - 1].append(this_method_count)
            method_args[interface_count - 1][this_method_count - 1] = []
            if tu_spelling[j + 2] == "*":
                method_name[interface_count - 1].append(tu_spelling[j + 4])
                method_return[interface_count - 1].append(tu_spelling[j + 1] + tu_spelling[j + 2])
            else:
                method_name[interface_count - 1].append(tu_spelling[j + 3])
                method_return[interface_count - 1].append(tu_spelling[j + 1])
            method_return[interface_count - 1][this_method_count - 1] = convert(method_return[interface_count - 1][this_method_count - 1])

        elif tu_spelling[j] == "(" and within_interface == 1 and within_method == 1:
            within_brackets = 1

        elif tu_spelling[j] == ")" and within_interface == 1 and within_method == 1 and within_brackets == 1:
            within_brackets = 0
            for k in range(len(method_args_content) - 1):
                if method_args_content[k] in struct_table:
                    method_args_content_string = method_args_content_string + "struct "
                method_args_content[k] = convert(method_args_content[k])
                method_args_content_string = method_args_content_string + method_args_content[k]
                if method_args_content[k + 1] != "," and method_args_content[k + 1] != "*" and method_args_content[k + 1] != "&"\
                        and method_args_content[k + 1] != ")" and method_args_content[k + 1] not in remove_table:
                    method_args_content_string = method_args_content_string + " "
            method_args[interface_count - 1][this_method_count - 1].append(method_args_content_string)
            method_args_content_string = ""
            method_args_content = []

        elif tu_spelling[j] == ";" and within_interface == 1 and within_method == 1:
            within_method = 0

        if tu_spelling[j] == "}" and within_interface == 1:
            interface_open_bracket = interface_open_bracket - 1
            if interface_open_bracket == 0:
                interface_location.append(tu_location[j])
                interface_token_location.append(j)
                within_interface = 0
                this_method_count = 0

        if within_brackets == 1:
            if tu_spelling[j] != ")":
                method_args_content.append(tu_spelling[j + 1])


        # ----- Structs ------------------------------------------------------------------

        if tu_spelling[j] == "struct" and tu_spelling[j + 2] == "{" and within_struct == 0:
            within_struct = 1
            struct_count = struct_count + 1
            struct_table.append(tu_spelling[j + 1])
            struct_content.append(struct_count + 1)
            struct_content[struct_count - 1] = []
            source_file_struct.append(i.cursor.translation_unit.spelling)

        elif tu_spelling[j] == "{" and within_struct == 1:
            struct_open_bracket = struct_open_bracket + 1

        elif tu_spelling[j] == "//------------------------------------------------------------------------"\
                and within_struct == 1 and within_struct_part == 0 and (tu_spelling[j + 1] in data_types or tu_spelling[j + 2] in data_types):
            within_struct_part = 1

        elif tu_spelling[j] == ("//------------------------------------------------------------------------"
                or tu_spelling[j] == "SMTG_CONSTEXPR14") and within_struct_part == 1 and within_struct == 1:
            within_struct_part = 0

        elif tu_spelling[j] in data_types and tu_spelling[j] != "*" and within_struct == 1 and within_struct_part == 1:
            temp = ""
            for k in range(100):
                if tu_spelling[j + k] != ":" and tu_spelling[j + k + 1] != ":":
                    if tu_spelling[j + k] not in struct_table and tu_spelling[j + k] != "::":
                        temp = temp + convert(tu_spelling[j + k])
                    if tu_spelling[j + k] != "[" and tu_spelling[j + k + 1] != "[" and tu_spelling[j + k + 1] != "]"\
                            and tu_spelling[j + k + 1] != ";" and tu_spelling[j + k] not in struct_table and tu_spelling[j + k] != "::":
                        temp = temp + " "
                if tu_spelling[j + k] == ";":
                    break
            struct_content[struct_count - 1].append(temp)

        if tu_spelling[j] == "}" and within_struct == 1:
            struct_open_bracket = struct_open_bracket - 1
            if struct_open_bracket == 0:
                within_struct = 0


        # ----- Enums ------------------------------------------------------------------

        if tu_spelling[j] == "enum" and (tu_spelling[j + 1] == "{" or tu_spelling[j + 2] == "{") and within_enum == 0:
            within_enum = 1

        elif tu_spelling[j] == "{" and within_enum == 1:
            enum_open_bracket = enum_open_bracket + 1

        if tu_spelling[j] == "}" and within_enum == 1:
            enum_open_bracket = enum_open_bracket - 1
            if enum_open_bracket == 0:
                within_enum = 0

        if within_enum == 1:
            if tu_spelling[j] == "=":
                enum_table.append(tu_spelling[j - 1])
                if tu_spelling[j + 2] == "," or tu_kind[j + 2] == tu_kind[j + 2].COMMENT or tu_spelling[j + 2] == "}":
                    enum_table.append(tu_spelling[j + 1])
                else:
                    temp = ""
                    temp = temp + tu_spelling[j + 1]
                    for k in range(100):
                        temp = temp + " "
                        temp = temp + tu_spelling[j + 2 + k]
                        if tu_spelling[j + 3 + k] == "," or tu_kind[j + 3 + k] is tu_kind[j + 3 + k].COMMENT or tu_spelling[j + 3 + k] == "}":
                            break
                    enum_table.append(temp)


        # ----- ID ------------------------------------------------------------------

        if tu_spelling[j] == "DECLARE_CLASS_IID" and tu_spelling[j - 1] != "define":
            for k in range(4):
                ID_table[interface_count - 1].append(tu_spelling[j + 2 * k + 4])

        #print(tu_spelling[j])
        #print(tu_location[j])
        #print("within_struct: ", within_struct)
        #print("within_struct_part: ", within_struct_part)
        #print("struct_open_bracket: ", struct_open_bracket)
        #print("within_enum: ", within_enum)
        #print("enum_open_bracket: ", enum_open_bracket)
        #print(" ")

        j = j + 1

    return interface_location, interface_token_location, method_count, struct_count, interface_count,\
           interface_name, method_name, method_return, method_args, interface_description, method_args_content,\
           struct_table, struct_content, inherits_table, ID_table, enum_table, data_types, source_file,\
           source_file_interface, source_file_struct


def convert(source):
    if source in enum_table:
        source = enum_table[enum_table.index(source) + 1]
    elif source in SMTG_table or source in SMTG_table_ptr or source in struct_table:
        source = "SMTG_{}".format(source)
    elif source in _t_table:
        source = "{}_t".format(source)
    elif source in _t_table_ptr:
        source = "{}_t*".format(_t_table[_t_table_ptr.index(source)])
    elif source in SMTG_TUID_table or source in SMTG_TUID_table_ptr:
        source = "SMTG_TUID"
    elif source == "_iid":
        source = "iid"
    elif source in remove_table:
        source = ""
    return source


def print_structs():
    for i in range(struct_count_includes, struct_count):
        print("//------------------------------------------------------------------------")
        if not only_print_current_header:
            print("// source: \"{}\"".format(source_file_struct[i]))
        print()
        print("struct SMTG_{} {}".format(struct_table[i], "{"))
        for j in range(len(struct_content[i])):
            print("    {}".format(struct_content[i][j]))
        print("};")
        print()


def print_methods(i):
    methods_location = 0
    for k in range(len(inherits_table[i])):
        if inherits_table[i][k] in interface_name:
            methods_location = interface_name.index(inherits_table[i][k])
        print("    // methods derived from \"{}\":".format(inherits_table[i][k]))
        for j in range(len(method_name[methods_location])):
            if method_args[methods_location][j][0] == "":
                print("    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);".format(method_return[methods_location][j],
                                                                                         method_name[methods_location][j]))
            elif method_args[methods_location][j][0] != "":

                print("    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});".format(method_return[methods_location][j],
                                                                                             method_name[methods_location][j],
                                                                                             method_args[methods_location][j][0]))
        print()
    print("    // methods defined in \"{}\":".format(interface_name[i]))
    for j in range(len(method_name[i])):
        if method_args[i][j][0] == "":
            print("    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);".format(method_return[i][j],
                                                                                           method_name[i][j]))
        elif method_args[i][j][0] != "":
            print("    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});".format(method_return[i][j],
                                                                                                   method_name[i][j],
                                                                                                   method_args[i][j][0]))
    print()


def print_interface():
    for i in range(interface_count_includes, interface_count):
        print("// ------------------------------------------------------------------------")
        print("// Steinberg::{}".format(interface_name[i]))
        if not only_print_current_header:
            print("// Source: \"{}\"".format(source_file_interface[i]))
        print("// ------------------------------------------------------------------------\n")
        print("typedef struct SMTG_{}Vtbl".format(interface_name[i]))
        print("{")
        print_methods(i)
        print("}", "SMTG_{}Vtbl;\n".format(interface_name[i]))
        print("typedef struct SMTG_{}".format(interface_name[i]))
        print("{")
        print("    SMTG_{}Vtbl* lpVtbl;".format(interface_name[i]))
        print("}", "SMTG_{};\n".format(interface_name[i]))
        print("SMTG_TUID SMTG_{}_iid = SMTG_INLINE_UID ({}, {}, {}, {});".format(interface_name[i],
                                                                                 ID_table[i][0],
                                                                                 ID_table[i][1],
                                                                                 ID_table[i][2],
                                                                                 ID_table[i][3]))
        print()

def print_standard():
    print("#include <stdint.h>\n")
    print("#define SMTG_STDMETHODCALLTYPE\n")
    print("#define SMTG_FUNKNOWN_C_GUTS \\")
    print("    SMTG_tresult (SMTG_STDMETHODCALLTYPE *queryInterface)(void* thisPointer, SMTG_TUID iid, void** ppv); \\")
    print("    uint32_t (SMTG_STDMETHODCALLTYPE *addRef)(void* thisPointer); \\")
    print("    uint32_t (SMTG_STDMETHODCALLTYPE *release)(void* thisPointer) \\\n")
    print("#if _WIN32 // COM_COMPATIBLE")
    print("#define SMTG_INLINE_UID(l1, l2, l3, l4) \\")
    print("{ \\")
    print("	(int8_t)(((uint32_t)(l1) & 0x000000FF)      ), (int8_t)(((uint32_t)(l1) & 0x0000FF00) >>  8), \\")
    print("	(int8_t)(((uint32_t)(l1) & 0x00FF0000) >> 16), (int8_t)(((uint32_t)(l1) & 0xFF000000) >> 24), \\")
    print("	(int8_t)(((uint32_t)(l2) & 0x00FF0000) >> 16), (int8_t)(((uint32_t)(l2) & 0xFF000000) >> 24), \\")
    print("	(int8_t)(((uint32_t)(l2) & 0x000000FF)      ), (int8_t)(((uint32_t)(l2) & 0x0000FF00) >>  8), \\")
    print("	(int8_t)(((uint32_t)(l3) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l3) & 0x00FF0000) >> 16), \\")
    print("	(int8_t)(((uint32_t)(l3) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l3) & 0x000000FF)      ), \\")
    print("	(int8_t)(((uint32_t)(l4) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l4) & 0x00FF0000) >> 16), \\")
    print("	(int8_t)(((uint32_t)(l4) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l4) & 0x000000FF)      )  \\")
    print("}")
    print("#else")
    print("#define SMTG_INLINE_UID(l1, l2, l3, l4) \\")
    print("{ \\")
    print("	(int8_t)(((uint32_t)(l1) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l1) & 0x00FF0000) >> 16), \\")
    print("	(int8_t)(((uint32_t)(l1) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l1) & 0x000000FF)      ), \\")
    print("	(int8_t)(((uint32_t)(l2) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l2) & 0x00FF0000) >> 16), \\")
    print("	(int8_t)(((uint32_t)(l2) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l2) & 0x000000FF)      ), \\")
    print("	(int8_t)(((uint32_t)(l3) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l3) & 0x00FF0000) >> 16), \\")
    print("	(int8_t)(((uint32_t)(l3) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l3) & 0x000000FF)      ), \\")
    print("	(int8_t)(((uint32_t)(l4) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l4) & 0x00FF0000) >> 16), \\")
    print("	(int8_t)(((uint32_t)(l4) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l4) & 0x000000FF)      )  \\")
    print("}")
    print("#endif\n")
    print("typedef uint8_t SMTG_TUID[16];")
    print("typedef int32_t SMTG_tresult;")
    print("typedef uint_least16_t SMTG_char16;")
    print("typedef uint8_t SMTG_char8;\n")
    print("//------------------------------------------------------------------------")
    print("// {}".format(source_file))
    print("//------------------------------------------------------------------------")
    print("")


def print_conversion():
    print_standard()
    print_structs()
    print_interface()


def print_info():
    for i in range(interface_count_includes, interface_count):
        print("Interface {}: {}".format(i + 1 - interface_count_includes, interface_name[i]))
        print("Source file: {}".format(source_file_interface[i]))
        print(interface_description[i])
        print("IID: {}, {}, {}, {}".format(ID_table[i][0], ID_table[i][1], ID_table[i][2], ID_table[i][3]))
        print("Inherits:")
        for j in range(len(inherits_table[i])):
            print(inherits_table[i][j])
        print("Token Location:", int(interface_token_location[2 * i]), "-",
              int(interface_token_location[2 * i + 1]))
        print("Start:", interface_location[2 * i])
        print("End:", interface_location[2 * i + 1])
        print("Methods found:", len(method_name[i]))
        for j in range(method_count):
            if j < len(method_name[i]):
                print(method_name[i][j])
        print("\r")







if __name__ == '__main__':

    only_print_current_header = False

    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()

    index = clang.cindex.Index.create()

    include_path = Path(sys.argv[1]).parents[2]
    print(include_path)

    tu = index.parse(filename[0], ['-I', str(include_path), '-x', 'c++-header'])

    source_file = tu.spelling

    includes_list = []
    interface_location = []
    interface_token_location = []
    interface_name = []
    method_name = []
    method_return = []
    method_args = []
    interface_description = []
    method_args_content = []
    struct_table = []
    struct_content = []
    inherits_table = []
    ID_table = []
    enum_table = []
    tu_table = []
    source_file_interface = []
    source_file_struct = []
    data_types = ["int32", "char8", "char16", "TUID", "uint32", "ParamID", "String128", "ParamValue", "UnitID"]
    remove_table = ["/*out*/", "/*in*/"]
    SMTG_table = ["tresult", "FUnknown", "char8", "char16", "IBStream", "ParamID", "ParamValue"]
    _t_table = ["int8", "int16", "int32", "int64", "int128", "uint8", "uint16", "uint32", "uint64", "uint128"]
    SMTG_TUID_table = ["FIDString", "TUID"]
    SMTG_table_ptr = []
    _t_table_ptr = []
    SMTG_TUID_table_ptr = []
    for i in range(len(SMTG_table)):
        SMTG_table_ptr.append(SMTG_table[i] + "*")
    for i in range(len(_t_table)):
        _t_table_ptr.append(_t_table[i] + "*")
    for i in range(len(SMTG_TUID_table)):
        SMTG_TUID_table_ptr.append(SMTG_TUID_table[i] + "*")

    method_count = 0
    struct_count = 0
    struct_count_includes = 0
    interface_count = 0
    interface_count_includes = 0

    l = 0

    tu_table.append(tu)

    for j in tu_table[0].get_includes():
        path = j.include
        path = str(path)
        if "C:\Program Files" not in path and path not in includes_list:
            #print("Path:", path)
            tu_table.append(index.parse(path, ['-I', str(include_path), '-x', 'c++-header']))
            includes_list.append(path)
            l = l + 1

    if only_print_current_header:
        tu_table.reverse()
    for i in tu_table:
        if only_print_current_header:
            interface_count_includes = interface_count
            struct_count_includes = struct_count
        interface_location, interface_token_location, method_count, struct_count, interface_count, \
        interface_name, method_name, method_return, method_args, interface_description, method_args_content,\
        struct_table, struct_content, inherits_table, ID_table, enum_table, data_types, source_file, source_file_interface,\
        source_file_struct = parsing(i, method_count, struct_count, interface_count, method_args, method_args_content)


    print_conversion()
    print_info()
    #for i in range(interface_count_includes, interface_count):
    #    print("Interface {}: {}".format(i + 1 - interface_count_includes, interface_name[i]))
    #    print("Source file: {}".format(source_file_interface[i]))
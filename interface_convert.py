import sys
from pathlib import Path
import clang.cindex
from clang.cindex import Config
from optparse import OptionParser

Config.set_library_path("venv/Lib/site-packages/clang/native")


# ----- preparse -------------------------------------------------------------------------------------------------------

def preparse_header(tu):
    for n in tu.get_children():
        if include_path in normalise_link(n.location.file) and normalise_link(n.location.file) not in includes_table_preparse:
            includes_table_preparse.append(normalise_link(n.location.file))
            preparse_namespace(n)
            preparsing(n)

def preparse_namespace(i):
    if i.kind == i.kind.NAMESPACE:
        for j in i.get_children():
            preparse_namespace(j)
            preparsing(j)

def preparsing(i):
    preparse_interfaces(i)
    preparse_structs(i)
    parse_typedefs(i)


def preparse_interfaces(i):
    if i.kind == i.kind.CLASS_DECL:
        interface_name_preparse.append(normalise_namespace(i.spelling))

def preparse_structs(i):
    if i.kind == i.kind.STRUCT_DECL:
        r = 0
        for j in i.get_children():
            if j.kind == j.kind.FIELD_DECL:
                if r == 0:
                    struct_table_preparse.append(i.spelling)
                r = r + 1

def parse_typedefs(i):
    if i.kind == i.kind.TYPEDEF_DECL:
        if i.spelling not in _t_table and i.spelling not in SMTG_TUID_table:
            typedef_name_preparse.append(i.spelling)
        typedef_name.append(convert(i.spelling))

        typedef_return.append(len(typedef_name) - 1)
        typedef_return[len(typedef_name) - 1] = []

        for j in i.get_children():
            typedef_return[len(typedef_name) - 1].append(convert(j.spelling))


# ----- parse ----------------------------------------------------------------------------------------------------------

def parse_header(tu):
    for n in tu.get_children():
        if include_path in normalise_link(n.location.file) and normalise_link(n.location.file) not in includes_table:
            includes_table.append(normalise_link(n.location.file))
            parse_namespace(n)
            parsing(n)

def parse_namespace(n):
        if n.kind == n.kind.NAMESPACE:
            for i in n.get_children():
                parse_namespace(i)
                parsing(i)

def parsing(i):
    parse_interfaces(i)
    parse_enum(i)
    parse_structs(i)


# ----- parse interfaces ---------------------------------------------------------------

def parse_interfaces(i):
    if i.kind == i.kind.CLASS_DECL:
        interface_source.append("Source: \"{}\", line {}".format(normalise_link(i.location.file), i.location.line))
        interface_description.append(i.brief_comment)
        interface_name.append(normalise_namespace(i.spelling))

        inherits_table.append(len(interface_name))
        inherits_table[len(interface_name) - 1] = []

        method_name.append(len(interface_name))
        method_name[len(interface_name) - 1] = []

        method_return.append(len(interface_name))
        method_return[len(interface_name) - 1] = []

        method_args.append(len(interface_name))
        method_args[len(interface_name) - 1] = []

        method_count_local = 0
        for j in i.get_children():
            parse_inheritance(j)
            method_count_local = parse_methods(j, method_count_local)


# ----- parse inheritances ---------------------------------------------------------------

def parse_inheritance(j):
    if j.kind == j.kind.CXX_BASE_SPECIFIER:
        for k in range(len(inherits_table[len(interface_name) - 1]) + 1):
            if normalise_namespace(j.type.spelling) in interface_name:
                inherits_location = interface_name.index(normalise_namespace(j.type.spelling))
                for n in range(len(inherits_table[inherits_location])):
                    inherits_table[len(interface_name) - 1].append(inherits_table[inherits_location][n])
        inherits_table[len(interface_name) - 1].append(normalise_namespace(j.type.spelling))


# ----- parse methods ---------------------------------------------------------------

def parse_methods(j, method_count_local):
    if j.kind == j.kind.CXX_METHOD:
        method_count_local = method_count_local + 1

        method_args[len(interface_name) - 1].append(method_count_local)
        method_args[len(interface_name) - 1][method_count_local - 1] = []

        method_name[len(interface_name) - 1].append(j.spelling)
        method_return[len(interface_name) - 1].append(convert(j.result_type.spelling))

        method_args_content = parse_method_arguments(j)
        method_args[len(interface_name) - 1][method_count_local - 1].append("".join(method_args_content))
    return method_count_local

def parse_method_arguments(j):
    p = 0
    method_args_content = []
    for k in j.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        if k.type.kind == k.type.kind.POINTER:
            method_args_content.append(convert(k.type.spelling))
        elif k.type.kind == k.type.kind.LVALUEREFERENCE or k.type.kind == k.type.kind.RVALUEREFERENCE:
            method_args_content.append(convert(k.type.spelling))
        else:
            method_args_content.append(convert(k.type.spelling))
        method_args_content.append(" ")
        method_args_content.append(convert(k.spelling))
        p = p + 1
    return method_args_content


# ----- parse structs ---------------------------------------------------------------

def parse_structs(i):
    if i.kind == i.kind.STRUCT_DECL:
        r = 0
        for j in i.get_children():
            parse_enum(j)
            if j.kind == j.kind.FIELD_DECL:
                struct_args = ""

                if r == 0:
                    struct_table.append(i.spelling)
                    struct_source.append("Source: \"{}\", line {}".format(normalise_link(i.location.file), i.location.line))
                    struct_content.append(len(struct_table) + 1)
                    struct_content[len(struct_table) - 1] = []
                struct_return = convert(j.type.spelling)

                for d in j.get_children():
                    if d.kind == d.kind.DECL_REF_EXPR:
                        struct_args = convert(d.spelling)

                if struct_args != "":
                    struct_content[len(struct_table) - 1].append(
                        "{} {} [{}];".format(struct_return, j.spelling, struct_args))
                else:
                    struct_content[len(struct_table) - 1].append("{} {};".format(struct_return, j.spelling))

                r = r + 1


# ----- parse enums ---------------------------------------------------------------

def parse_enum(i):
    if i.kind == i.kind.ENUM_DECL:
        enum_name.append(i.spelling)
        enum_table.append(len(enum_name) - 1)
        enum_table[len(enum_name) - 1] = []
        enum_source.append("Source: {}, line {}".format(normalise_link(i.location.file), i.location.line))

        for j in i.get_children():
            if j.kind == j.kind.ENUM_CONSTANT_DECL:
                #print(j.spelling)
                #print("", j.enum_value)
                enum_table[len(enum_name) - 1].append(j.spelling)
                enum_table_l.append(j.spelling)
                parse_enum_value(j)

def parse_enum_value(i):
    children = False
    for j in i.get_children():
        children = True
        if j.kind == j.kind.INTEGER_LITERAL or j.kind == j.kind.BINARY_OPERATOR:
            if array_to_string(get_values_in_extent(j), True) != "":
                enum_table[len(enum_name) - 1].append(array_to_string(get_values_in_extent(j), True))
                enum_table_r.append(array_to_string(get_values_in_extent(j), True))
        elif j.kind == j.kind.UNEXPOSED_EXPR:
            parse_enum_value(j)
        else:
            enum_table[len(enum_name) - 1].append("nil")
            enum_table_r.append("nil")
    if children == False:
        enum_table[len(enum_name) - 1].append("nil")
        enum_table_r.append("nil")


# ----- print functions ------------------------------------------------------------------------------------------------

def print_standard():
    print("// ----------------------------------------------------------------------------------------------------")
    print("// Source file: {}".format(source_file))
    print("// ----------------------------------------------------------------------------------------------------")
    print()
    print("#include <stdint.h>")
    print()
    print("#define SMTG_STDMETHODCALLTYPE")
    print()
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
    print("#endif")
    print()
    print("// ----------------------------------------------------------------------------------------------------")
    print("// Typedefs")
    print("// ----------------------------------------------------------------------------------------------------")
    print()
    print("typedef uint8_t SMTG_TUID[16];")
    print("typedef uint_least16_t SMTG_char16;")
    print("typedef uint8_t SMTG_char8;")
    print_typedefs()
    print()
    print()

def print_typedefs():
    for i in range(len(typedef_name)):
        if typedef_return[i] != []:
            print("typedef {} {};".format(typedef_return[i][0], typedef_name[i]))

def print_interface_forward():
    print("// ----------------------------------------------------------------------------------------------------")
    print("// Interface forward declarations")
    print("// ----------------------------------------------------------------------------------------------------")
    print()
    for i in range(len(interface_name)):
        print("typedef struct {};".format(interface_name[i]))
    print()
    print()

def print_enums():
    print("// ----------------------------------------------------------------------------------------------------")
    print("// Enums")
    print("// ----------------------------------------------------------------------------------------------------")
    print()
    for i in range(len(enum_table)):
        print("// ----------------------------------------------------------------------------------------------------")
        print("// {}".format(enum_source[i]))
        print()
        if enum_name[i] == "":
            print("enum")
        else:
            print("enum SMTG_{}". format(enum_name[i]))
        print("{")
        for j in range(int(len(enum_table[i]) / 2)):
            if j < int(len(enum_table[i]) / 2) - 1:
                if enum_table[i][2 * j + 1] != "nil":
                    print("{} = {},".format(enum_table[i][2 * j], enum_table[i][2 * j + 1]))
                else:
                    print("{},".format(enum_table[i][2 * j]))
            else:
                if enum_table[i][2 * j + 1] != "nil":
                    print("{} = {}".format(enum_table[i][2 * j], enum_table[i][2 * j + 1]))
                else:
                    print("{}".format(enum_table[i][2 * j]))
        print("};")
        print()
    print()

def print_structs():
    print("// ----------------------------------------------------------------------------------------------------")
    print("// Structs")
    print("// ----------------------------------------------------------------------------------------------------")
    print()
    for i in range(len(struct_table)):
        print("// ----------------------------------------------------------------------------------------------------")
        print("// {}".format(struct_source[i]))
        print()
        print("struct SMTG_{} {}".format(struct_table[i], "{"))
        for j in range(len(struct_content[i])):
            print("    {}".format(struct_content[i][j]))
        print("};")
        print()
    print()

def print_methods(i):
    methods_location = 0
    for k in range(len(inherits_table[i])):
        if inherits_table[i][k] in interface_name:
            methods_location = interface_name.index(inherits_table[i][k])
        print("    // methods derived from \"{}\":".format(inherits_table[i][k]))
        for j in range(len(method_name[methods_location])):
            if method_args[methods_location][j][0] == "":
                print("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);".format(method_return[methods_location][j],
                                                                                         method_name[methods_location][j]))
            elif method_args[methods_location][j][0] != "":

                print("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});".format(method_return[methods_location][j],
                                                                                             method_name[methods_location][j],
                                                                                             method_args[methods_location][j][0]))
        print()
    print("    // methods defined in \"{}\":".format(interface_name[i]))
    for j in range(len(method_name[i])):
        if method_args[i][j][0] == "":
            print("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);".format(method_return[i][j],
                                                                                           method_name[i][j]))
        elif method_args[i][j][0] != "":
            print("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});".format(method_return[i][j],
                                                                                                   method_name[i][j],
                                                                                                   method_args[i][j][0]))
    print()

def print_interface():
    print("// ----------------------------------------------------------------------------------------------------")
    print("// Interfaces")
    print("// ----------------------------------------------------------------------------------------------------")
    print()
    for i in range(len(interface_name)):
        print("// ----------------------------------------------------------------------------------------------------")
        #print("// Steinberg::{}".format(interface_name[i]))
        print("// {}".format(interface_source[i]))
        print()
        print("typedef struct SMTG_{}Vtbl".format(interface_name[i]))
        print("{")
        print_methods(i)
        print("}", "SMTG_{}Vtbl;".format(interface_name[i]))
        print()
        print("typedef struct SMTG_{}".format(interface_name[i]))
        print("{")
        print("    SMTG_{}Vtbl* lpVtbl;".format(interface_name[i]))
        print("}", "SMTG_{};".format(interface_name[i]))
        print()
        #print("SMTG_TUID SMTG_{}_iid = SMTG_INLINE_UID ({}, {}, {}, {});".format(interface_name[i],
        #                                                                         ID_table[i][0],
        #                                                                         ID_table[i][1],
        #                                                                         ID_table[i][2],
        #                                                                         ID_table[i][3]))
        print()
    print()

def print_info():
    for i in range(len(interface_name)):
        print("Interface {}: {}".format(i + 1, interface_name[i]))
        print(interface_source[i])
        print("Info:", interface_description[i])
        print("Inherits:")
        for j in range(len(inherits_table[i])):
            print(" ", inherits_table[i][j])
        print("Methods:")
        for j in range(len(method_name[i])):
            print(" ", method_name[i][j])
        print()
    print()

def print_conversion():
    print_standard()
    print_interface_forward()
    print_enums()
    print_structs()
    print_interface()
    print_info()


# ----- write functions ------------------------------------------------------------------------------------------------

def write_standard():
    h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
    h.write("Source file: {}\n".format(source_file))
    h.write("----------------------------------------------------------------------------------------------------------------------*/\n")
    h.write("\n")
    h.write("#include <stdint.h>\n")
    h.write("\n")
    h.write("#define SMTG_STDMETHODCALLTYPE\n")
    h.write("\n")
    h.write("#if _WIN32 /* COM_COMPATIBLE */\n")
    h.write("#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n")
    h.write("{ \\\n")
    h.write("	(int8_t)(((uint32_t)(l1) & 0x000000FF)      ), (int8_t)(((uint32_t)(l1) & 0x0000FF00) >>  8), \\\n")
    h.write("	(int8_t)(((uint32_t)(l1) & 0x00FF0000) >> 16), (int8_t)(((uint32_t)(l1) & 0xFF000000) >> 24), \\\n")
    h.write("	(int8_t)(((uint32_t)(l2) & 0x00FF0000) >> 16), (int8_t)(((uint32_t)(l2) & 0xFF000000) >> 24), \\\n")
    h.write("	(int8_t)(((uint32_t)(l2) & 0x000000FF)      ), (int8_t)(((uint32_t)(l2) & 0x0000FF00) >>  8), \\\n")
    h.write("	(int8_t)(((uint32_t)(l3) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l3) & 0x00FF0000) >> 16), \\\n")
    h.write("	(int8_t)(((uint32_t)(l3) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l3) & 0x000000FF)      ), \\\n")
    h.write("	(int8_t)(((uint32_t)(l4) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l4) & 0x00FF0000) >> 16), \\\n")
    h.write("	(int8_t)(((uint32_t)(l4) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l4) & 0x000000FF)      )  \\\n")
    h.write("}\n")
    h.write("#else\n")
    h.write("#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n")
    h.write("{ \\\n")
    h.write("	(int8_t)(((uint32_t)(l1) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l1) & 0x00FF0000) >> 16), \\\n")
    h.write("	(int8_t)(((uint32_t)(l1) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l1) & 0x000000FF)      ), \\\n")
    h.write("	(int8_t)(((uint32_t)(l2) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l2) & 0x00FF0000) >> 16), \\\n")
    h.write("	(int8_t)(((uint32_t)(l2) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l2) & 0x000000FF)      ), \\\n")
    h.write("	(int8_t)(((uint32_t)(l3) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l3) & 0x00FF0000) >> 16), \\\n")
    h.write("	(int8_t)(((uint32_t)(l3) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l3) & 0x000000FF)      ), \\\n")
    h.write("	(int8_t)(((uint32_t)(l4) & 0xFF000000) >> 24), (int8_t)(((uint32_t)(l4) & 0x00FF0000) >> 16), \\\n")
    h.write("	(int8_t)(((uint32_t)(l4) & 0x0000FF00) >>  8), (int8_t)(((uint32_t)(l4) & 0x000000FF)      )  \\\n")
    h.write("}\n")
    h.write("#endif\n")
    h.write("\n")
    h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
    h.write("Typedefs\n")
    h.write("----------------------------------------------------------------------------------------------------------------------*/\n")
    h.write("\n")
    h.write("typedef uint8_t SMTG_TUID[16];\n")
    h.write("typedef uint_least16_t SMTG_char16;\n")
    h.write("typedef uint8_t SMTG_char8;\n")
    write_typedefs()
    h.write("\n")
    h.write("\n")

def write_typedefs():
    for i in range(len(typedef_name)):
        if typedef_return[i] != []:
            h.write("typedef {} {};\n".format(typedef_return[i][0], typedef_name[i]))

def write_interface_forward():
    h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
    h.write("Interface forward declarations\n")
    h.write("----------------------------------------------------------------------------------------------------------------------*/\n")
    h.write("\n")
    for i in range(len(interface_name)):
        h.write("typedef struct {};\n".format(interface_name[i]))
    h.write("\n")
    h.write("\n")

def write_enums():
    h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
    h.write("Enums\n")
    h.write("----------------------------------------------------------------------------------------------------------------------*/\n")
    h.write("\n")
    for i in range(len(enum_table)):
        h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
        h.write("{} */\n".format(enum_source[i]))
        h.write("\n")
        if enum_name[i] == "":
            h.write("enum\n")
        else:
            h.write("enum SMTG_{}\n".format(enum_name[i]))
        h.write("{\n")
        for j in range(int(len(enum_table[i]) / 2)):
            if j < int(len(enum_table[i]) / 2) - 1:
                if enum_table[i][2 * j + 1] != "nil":
                    h.write("{} = {},\n".format(enum_table[i][2 * j], enum_table[i][2 * j + 1]))
                else:
                    h.write("{},\n".format(enum_table[i][2 * j]))
            else:
                if enum_table[i][2 * j + 1] != "nil":
                    h.write("{} = {}\n".format(enum_table[i][2 * j], enum_table[i][2 * j + 1]))
                else:
                    h.write("{}\n".format(enum_table[i][2 * j]))
        h.write("};\n")
        h.write("\n")
    h.write("\n")

def write_structs():
    h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
    h.write("Structs\n")
    h.write("----------------------------------------------------------------------------------------------------------------------*/\n")
    h.write("\n")
    for i in range(len(struct_table)):
        h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
        h.write("{} */\n".format(struct_source[i]))
        h.write("\n")
        h.write("struct SMTG_{} {}\n".format(struct_table[i], "{"))
        for j in range(len(struct_content[i])):
            h.write("    {}\n".format(struct_content[i][j]))
        h.write("};\n")
        h.write("\n")
    h.write("\n")

def write_interface():
    h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
    h.write("Interfaces\n")
    h.write("----------------------------------------------------------------------------------------------------------------------*/\n")
    h.write("\n")
    for i in range(len(interface_name)):
        h.write("/*----------------------------------------------------------------------------------------------------------------------\n")
        #h.write("Steinberg::{}\n".format(interface_name[i]))
        h.write("{} */\n".format(interface_source[i]))
        h.write("\n")
        h.write("typedef struct SMTG_{}Vtbl\n".format(interface_name[i]))
        h.write("{\n")
        write_methods(i)
        h.write("{} SMTG_{}Vtbl;\n".format("}", interface_name[i]))
        h.write("\n")
        h.write("typedef struct SMTG_{}\n".format(interface_name[i]))
        h.write("{\n")
        h.write("    SMTG_{}Vtbl* lpVtbl;\n".format(interface_name[i]))
        h.write("{} SMTG_{};\n".format("}", interface_name[i]))
        h.write("\n")
        # h.write("SMTG_TUID SMTG_{}_iid = SMTG_INLINE_UID ({}, {}, {}, {});".format(interface_name[i],
        #                                                                         ID_table[i][0],
        #                                                                         ID_table[i][1],
        #                                                                         ID_table[i][2],
        #                                                                         ID_table[i][3]))
        h.write("\n")
    h.write("\n")

def write_methods(i):
    methods_location = 0
    for k in range(len(inherits_table[i])):
        if inherits_table[i][k] in interface_name:
            methods_location = interface_name.index(inherits_table[i][k])
        h.write("    /* methods derived from \"{}\": */\n".format(inherits_table[i][k]))
        for j in range(len(method_name[methods_location])):
            if method_args[methods_location][j][0] == "":
                h.write("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);\n".format(
                    method_return[methods_location][j],
                    method_name[methods_location][j]))
            elif method_args[methods_location][j][0] != "":

                h.write("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});\n".format(
                    method_return[methods_location][j],
                    method_name[methods_location][j],
                    method_args[methods_location][j][0]))
        h.write("\n")
    h.write("    /* methods defined in \"{}\": */\n".format(interface_name[i]))
    for j in range(len(method_name[i])):
        if method_args[i][j][0] == "":
            h.write("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);\n".format(method_return[i][j],
                                                                                              method_name[i][j]))
        elif method_args[i][j][0] != "":
            h.write("    virtual {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});\n".format(method_return[i][j],
                                                                                                method_name[i][j],
                                                                                                method_args[i][j][
                                                                                                    0]))
    h.write("\n")


def write_conversion():
    write_standard()
    write_interface_forward()
    write_enums()
    write_structs()
    write_interface()


# ----- utility functions ----------------------------------------------------------------------------------------------

def normalise_link(source):
    source = str(source)
    return source.replace("\\", "/")

def normalise_namespace(source):
    source = str(source)
    #print(source)
    if "::" in source:
        source = source[source.index("::") + 2:]
        #print(" ", source)
        source = normalise_namespace(source)
    #print()
    return source

def normalise_args(source):
    source = str(source)
    if "[" in source:
        source = source[:source.index("[")]
    return source

def remove_spaces(source):
    source = str(source)
    if " " in source:
        source = source.replace(" ", "")
    return source

def array_to_string(array, spaces):
    string = ""
    if spaces:
        for i in range(len(array)):
                if i != 0:
                    string = string + " "
                string = string + array[i]
    else:
        string = "".join(array)
    return string

def get_values_in_extent(i):
    values = []
    for j in i.get_tokens():
        values.append(j.spelling)
    return values

def create_pointer_lists():
    for i in SMTG_table:
        SMTG_table_ptr.append(i + "*")
        SMTG_table_double_ptr.append(i + "**")
        SMTG_table_lvr.append(i + "&")
        SMTG_table_rvr.append(i + "&&")
    for i in _t_table:
        _t_table_ptr.append(i + "*")
        _t_table_double_ptr.append(i + "**")
        _t_table_lvr.append(i + "&")
        _t_table_rvr.append(i + "&&")
    for i in SMTG_TUID_table:
        SMTG_TUID_table_ptr.append(i + "*")
        SMTG_TUID_table_double_ptr.append(i + "**")
        SMTG_TUID_table_ptr.append(i + "&")
        SMTG_TUID_table_double_ptr.append(i + "&&")
    for i in interface_name_preparse:
        interface_name_preparse_ptr.append(i + "*")
        interface_name_preparse_double_ptr.append(i + "**")
        interface_name_preparse_lvr.append(i + "&")
        interface_name_preparse_rvr.append(i + "&&")
    for i in struct_table_preparse:
        struct_table_preparse_ptr.append(i + "*")
        struct_table_preparse_double_ptr.append(i + "**")
        struct_table_preparse_lvr.append(i + "&")
        struct_table_preparse_rvr.append(i + "&&")


# ----- conversion function --------------------------------------------------------------------------------------------

def convert(source):
    found_const = False
    source = str(source)
    #print(source)
    if "const " in source:
        source = source.replace("const ", "")
        found_const = True
    source = normalise_args(source)
    source = remove_spaces(source)
    source = normalise_namespace(source)
    #print("  ", source)
    if source in enum_table_l and not source.isnumeric():
        source = convert(enum_table_r[enum_table_l.index(source)])

    elif source in _t_table:
        source = "{}_t".format(source)
    elif source in _t_table_double_ptr:
        source = "{}_t**".format(source.replace("**", ""))
    elif source in _t_table_ptr:
        source = "{}_t*".format(source.replace("*", ""))
    elif source in _t_table_rvr:
        source = "{}_t&&".format(source.replace("&&", ""))
    elif source in _t_table_lvr:
        source = "{}_t&".format(source.replace("&", ""))

    elif source in SMTG_TUID_table or source in SMTG_TUID_table_ptr:
        source = "SMTG_TUID"
    elif source in SMTG_TUID_table_double_ptr:
        source = "SMTG_TUID**".format(source.replace("**", ""))
    elif source in SMTG_TUID_table_ptr:
        source = "SMTG_TUID*".format(source.replace("*", ""))
    elif source in SMTG_TUID_table_rvr:
        source = "SMTG_TUID&&".format(source.replace("&&", ""))
    elif source in SMTG_TUID_table_rvr:
        source = "SMTG_TUID&".format(source.replace("&", ""))

    elif source in SMTG_table or source in SMTG_table_ptr or source in struct_table_preparse or source in interface_name_preparse or source in typedef_name_preparse:
        source = "SMTG_{}".format(source)
    elif source in SMTG_table_double_ptr or source in struct_table_preparse_double_ptr or source in interface_name_preparse_double_ptr:
        source = "SMTG_{}**".format(source.replace("**", ""))
    elif source in SMTG_table_ptr or source in struct_table_preparse_ptr or source in interface_name_preparse_ptr:
        source = "SMTG_{}*".format(source.replace("*", ""))
    elif source in SMTG_table_rvr or source in struct_table_preparse_rvr or source in interface_name_preparse_rvr:
        source = "SMTG_{}&&".format(source.replace("&&", ""))
    elif source in SMTG_table_lvr or source in struct_table_preparse_lvr or source in interface_name_preparse_lvr:
        source = "SMTG_{}&".format(source.replace("&", ""))

    elif source == "_iid":
        source = "iid"
    elif source in remove_table:
        source = ""
    if found_const:
        source = "const {}".format(source)
    #print("     ", source)
    #print()
    return source







if __name__ == '__main__':

    print_header = True
    write_header = True


# ----- Establish Translation Unit -----
    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()
    index = clang.cindex.Index.create()
    include_path = normalise_link(Path(sys.argv[1]).parents[2])
    tu = index.parse(normalise_link(filename[0]), ['-I', include_path, '-x', 'c++-header'])
    source_file = normalise_link(tu.spelling)

# ----- Arrays -----
    interface_source = []
    interface_description = []
    interface_name = []
    interface_name_preparse = []
    inherits_table = []
    tu_table_temp = []
    tu_table_spelling = []
    tu_table = []
    includes_list = []
    includes_table = []
    includes_table_preparse = []
    method_name = []
    method_return = []
    method_args = []
    struct_table = []
    struct_table_preparse = []
    struct_content = []
    struct_source = []
    enum_name = []
    enum_table = []
    enum_table_l = []
    enum_table_r = []
    enum_source = []
    typedef_name = []
    typedef_name_preparse = []
    typedef_return = []


# ----- Conversion arrays -----
    data_types = ["int32", "char8", "char16", "TUID", "uint32", "ParamID", "String128", "ParamValue", "UnitID"]
    remove_table = ["/*out*/", "/*in*/"]
    SMTG_table = ["char8", "char16", "char32", "char64", "char128"]
    _t_table = ["int8", "int16", "int32", "int64", "int128", "uint8", "uint16", "uint32", "uint64", "uint128"]
    SMTG_TUID_table = ["FIDString", "TUID"]

    SMTG_table_ptr = []
    SMTG_table_double_ptr = []
    SMTG_table_lvr = []
    SMTG_table_rvr = []

    _t_table_ptr = []
    _t_table_double_ptr = []
    _t_table_lvr = []
    _t_table_rvr = []

    SMTG_TUID_table_ptr = []
    SMTG_TUID_table_double_ptr = []
    SMTG_TUID_table_lvr = []
    SMTG_TUID_table_rvr = []

    interface_name_preparse_ptr = []
    interface_name_preparse_double_ptr = []
    interface_name_preparse_lvr = []
    interface_name_preparse_rvr = []

    struct_table_preparse_ptr = []
    struct_table_preparse_double_ptr = []
    struct_table_preparse_lvr = []
    struct_table_preparse_rvr = []


# ----- Parsing -----
    preparse_header(tu.cursor)
    create_pointer_lists()
    parse_header(tu.cursor)

# ----- Print -----
    if print_header:
        print_conversion()

# ----- Write -----
    if write_header:
        header_path = "test_header.h"
        with open(header_path, 'w') as h:
            write_conversion()

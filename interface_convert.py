import sys
from pathlib import Path
from clang.cindex import Config, Index, TokenGroup
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
    preparse_enum(i)
    preparse_structs(i)
    parse_typedefs(i)


def preparse_interfaces(i):
    if i.kind == i.kind.CLASS_DECL:
        interface_name_preparse.append(normalise_namespace(i.spelling))
        for j in i.get_children():
            #parse_typedefs(j)
            preparse_enum(j)

def preparse_enum(i):
    if i.kind == i.kind.ENUM_DECL:
        enum_name_preparse.append(i.spelling)

def preparse_structs(i):
    if i.kind == i.kind.STRUCT_DECL:
        r = 0
        for j in i.get_children():
            preparse_enum(j)
            if j.kind == j.kind.FIELD_DECL:
                if r == 0:
                    struct_table_preparse.append(i.spelling)
                r = r + 1

def parse_typedefs(i):
    if i.kind == i.kind.TYPEDEF_DECL:
        if i.spelling not in SMTG_TUID_table:
            typedef_name_preparse.append(i.spelling)

        if i.underlying_typedef_type.kind == i.type.kind.CONSTANTARRAY:
            typedef_return.append(convert(i.underlying_typedef_type.element_type.spelling))
            typedef_name.append("{}[{}]".format(convert(i.spelling), i.underlying_typedef_type.element_count))
        else:
            typedef_return.append(convert(i.underlying_typedef_type.spelling))
            typedef_name.append(convert(i.spelling))


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
    parse_IID(i)

def parse_IID(i):
    if i.kind == i.kind.VAR_DECL and i.spelling.endswith("_iid"):
        ID_tokens = get_tokens_from_extent(i)
        ID_table[ID_tokens[2]] = [ID_tokens[4], ID_tokens[6], ID_tokens[8], ID_tokens[10]]

def get_tokens_from_extent(cursor):
    tu = cursor.translation_unit
    extent = tu.get_extent(cursor.location.file.name, [cursor.extent.start.offset, cursor.extent.end.offset])
    return [token.spelling for token in TokenGroup.get_tokens(tu, extent)]

# ----- parse interfaces ---------------------------------------------------------------

def parse_interfaces(i):
    if i.kind == i.kind.CLASS_DECL and i.spelling not in blacklist:
        children = list(i.get_children())
        if not children:
            return
        interface_source.append("Source: \"{}\", line {}".format(normalise_link(i.location.file), i.location.line))
        interface_description.append(i.brief_comment)
        interface_name.append(normalise_namespace(i.spelling))
        position = len(interface_name) - 1

        inherits_table.append("")
        inherits_table[position] = []

        method_name.append("")
        method_name[position] = []

        method_return.append("")
        method_return[position] = []

        method_args.append("")
        method_args[position] = []

        method_count_local = 0
        for j in children:
            parse_enum(j)
            parse_inheritance(j)
            method_count_local = parse_methods(j, method_count_local, interface_name[-1])


# ----- parse inheritances ---------------------------------------------------------------

def parse_inheritance(j):
    if j.kind == j.kind.CXX_BASE_SPECIFIER:
        position = len(interface_name) - 1
        for k in range(len(inherits_table[position]) + 1):
            if normalise_namespace(j.type.spelling) in interface_name:
                inherits_location = interface_name.index(normalise_namespace(j.type.spelling))
                for n in range(len(inherits_table[inherits_location])):
                    inherits_table[position].append(inherits_table[inherits_location][n])
        inherits_table[position].append(normalise_namespace(j.type.spelling))


# ----- parse methods ---------------------------------------------------------------

def parse_methods(j, method_count_local, current_interface):
    if j.kind == j.kind.CXX_METHOD:
        method_count_local = method_count_local + 1
        position = len(interface_name) - 1

        method_args[position].append("")
        method_args[position][method_count_local - 1] = []

        method_name[position].append(j.spelling)

        method_return[position].append(convert(get_underlying_type(j, j.result_type, current_interface)))
        method_args_content = parse_method_arguments(j, current_interface)
        method_args[position][method_count_local - 1].append("".join(method_args_content))
    return method_count_local

def get_namespaces(source):
    if "const " in source:
        source = source.replace("const ", "")
    return source.split("::")[:-1]


def parse_method_arguments(j, current_interface):
    p = 0
    method_args_content = []
    for k in j.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        method_args_content.append(convert(get_underlying_type(k, k.type, current_interface)))
        method_args_content.append(" ")
        method_args_content.append(convert(k.spelling))
        p = p + 1
    return method_args_content

def get_underlying_type(cursor, type, current_interface):
    if type.kind == type.kind.ENUM:
        return type.spelling
    namespaces = get_namespaces(type.spelling)
    if namespaces and namespaces[-1] == current_interface:
        if type.kind == type.kind.LVALUEREFERENCE:
            result_type = list(cursor.get_children())[0].type
            suffix = " &"
        elif type.kind == type.kind.LVALUEREFERENCE or type.kind == type.kind.RVALUEREFERENCE:
            result_type = list(cursor.get_children())[0].type
            suffix = " &&"
        elif type.kind == type.kind.POINTER:
            result_type = type.get_pointee()
            suffix = " *"
            if result_type.kind == type.kind.POINTER:
                result_type = result_type.get_pointee()
                suffix += "*"
        else:
            result_type = type
            suffix = ""
        return result_type.get_declaration().underlying_typedef_type.spelling + suffix
    else:
        return type.spelling

# ----- parse structs ---------------------------------------------------------------

def parse_structs(i):
    if i.kind == i.kind.STRUCT_DECL and i.spelling not in blacklist:
        r = 0
        position = len(struct_table) - 1
        for j in i.get_children():
            parse_enum(j)
            if j.kind == j.kind.FIELD_DECL:
                struct_args = ""

                if r == 0:
                    struct_table.append(i.spelling)
                    position = len(struct_table) - 1
                    struct_source.append("Source: \"{}\", line {}".format(normalise_link(i.location.file), i.location.line))
                    struct_content.append("")
                    struct_content[position] = []
                if j.type.kind == j.type.kind.CONSTANTARRAY:
                    struct_return = convert(j.type.element_type.spelling)
                else:
                    struct_return = convert(j.type.spelling)

                for d in j.get_children():
                    if d.kind == d.kind.DECL_REF_EXPR:
                        struct_args = convert(d.spelling)

                if struct_args != "":
                    struct_content[position].append(
                        "{} {} [{}];".format(struct_return, j.spelling, struct_args))
                else:
                    struct_content[position].append("{} {};".format(struct_return, j.spelling))

                r = r + 1


# ----- parse enums ---------------------------------------------------------------

def parse_enum(i):
    if i.kind == i.kind.ENUM_DECL:
        enum_name.append(i.spelling)
        position = len(enum_name) - 1
        enum_table.append("")
        enum_table[position] = []
        enum_source.append("Source: {}, line {}".format(normalise_link(i.location.file), i.location.line))

        for j in i.get_children():
            if j.kind == j.kind.ENUM_CONSTANT_DECL:
                enum_table[position].append(j.spelling)
                enum_table_l.append(j.spelling)
                parse_enum_value(j)

def parse_enum_value(i):
    children = False
    position = len(enum_name) - 1
    for j in i.get_children():
        children = True
        if j.kind == j.kind.INTEGER_LITERAL or j.kind == j.kind.BINARY_OPERATOR:
            if array_to_string(get_values_in_extent(j), True) != "":
                enum_table[position].append(array_to_string(get_values_in_extent(j), True))
                enum_table_r.append(array_to_string(get_values_in_extent(j), True))
        elif j.kind == j.kind.UNEXPOSED_EXPR:
            parse_enum_value(j)
        else:
            enum_table[position].append("nil")
            enum_table_r.append("nil")
    if children == False:
        enum_table[position].append("nil")
        enum_table_r.append("nil")


# ----- output to string ------------------------------------------------------------------------------------------------

def generate_standard():
    result = "/*----------------------------------------------------------------------------------------------------------------------\n"
    result += "Source file: {}\n".format(source_file)
    result += "----------------------------------------------------------------------------------------------------------------------*/\n"
    result += "\n"
    result += "#include <stdint.h>\n"
    result += "\n"
    result += "#define SMTG_STDMETHODCALLTYPE\n"
    result += "\n"
    result += "#if _WIN32 /* COM_COMPATIBLE */\n"
    result += "#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n"
    result += "{ \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0x000000FF)      ), (SMTG_int8)(((SMTG_uint32)(l1) & 0x0000FF00) >>  8), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0x00FF0000) >> 16), (SMTG_int8)(((SMTG_uint32)(l1) & 0xFF000000) >> 24), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0x00FF0000) >> 16), (SMTG_int8)(((SMTG_uint32)(l2) & 0xFF000000) >> 24), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0x000000FF)      ), (SMTG_int8)(((SMTG_uint32)(l2) & 0x0000FF00) >>  8), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l3) & 0x00FF0000) >> 16), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l3) & 0x000000FF)      ), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l4) & 0x00FF0000) >> 16), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l4) & 0x000000FF)      )  \\\n"
    result += "}\n"
    result += "#else\n"
    result += "#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n"
    result += "{ \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l1) & 0x00FF0000) >> 16), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l1) & 0x000000FF)      ), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l2) & 0x00FF0000) >> 16), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l2) & 0x000000FF)      ), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l3) & 0x00FF0000) >> 16), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l3) & 0x000000FF)      ), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l4) & 0x00FF0000) >> 16), \\\n"
    result += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l4) & 0x000000FF)      )  \\\n"
    result += "}\n"
    result += "#endif\n"
    result += "\n"
    result += "/*----------------------------------------------------------------------------------------------------------------------\n"
    result += "Typedefs\n"
    result += "----------------------------------------------------------------------------------------------------------------------*/\n"
    result += "\n"
    result += generate_typedefs()
    result += "\n"
    result += "\n"
    return result

def generate_typedefs():
    result = ""
    for i in range(len(typedef_name)):
        if typedef_return[i] != [] and typedef_name[i] not in blacklist:
            result += "typedef {} {};\n".format(typedef_return[i], typedef_name[i])
    return result

def generate_interface_forward():
    result = ""
    result += "/*----------------------------------------------------------------------------------------------------------------------\n"
    result += "Interface forward declarations\n"
    result += "----------------------------------------------------------------------------------------------------------------------*/\n"
    result += "\n"
    for i in range(len(interface_name)):
        result += "typedef struct {};\n".format(convert(interface_name[i]))
    result += "\n"
    for i in range(len(struct_table)):
        result += "typedef struct {};\n".format(convert(struct_table[i]))
    result += "\n"
    result += "\n"
    return result

def generate_enums():
    result = ""
    result += "/*----------------------------------------------------------------------------------------------------------------------\n"
    result += "Enums\n"
    result += "----------------------------------------------------------------------------------------------------------------------*/\n"
    result += "\n"
    for i in range(len(enum_table)):
        if enum_name[i] == "":
            continue
        result += "/*----------------------------------------------------------------------------------------------------------------------\n"
        result += "{} */\n".format(enum_source[i])
        result += "\n"
        result += "enum SMTG_{}\n".format(enum_name[i])
        result += "{\n"
        for j in range(int(len(enum_table[i]) / 2)):
            if j < int(len(enum_table[i]) / 2) - 1:
                if enum_table[i][2 * j + 1] != "nil":
                    result += "{} = {},\n".format(enum_table[i][2 * j], enum_table[i][2 * j + 1])
                else:
                    result += "{},\n".format(enum_table[i][2 * j])
            else:
                if enum_table[i][2 * j + 1] != "nil":
                    result += "{} = {}\n".format(enum_table[i][2 * j], enum_table[i][2 * j + 1])
                else:
                    result += "{}\n".format(enum_table[i][2 * j])
        result += "};\n"
        result += "\n"
    result += "\n"
    return result

def generate_structs():
    result = ""
    result += "/*----------------------------------------------------------------------------------------------------------------------\n"
    result += "Structs\n"
    result += "----------------------------------------------------------------------------------------------------------------------*/\n"
    result += "\n"
    for i in range(len(struct_table)):
        result += "/*----------------------------------------------------------------------------------------------------------------------\n"
        result += "{} */\n".format(struct_source[i])
        result += "\n"
        result += "struct SMTG_{} {}\n".format(struct_table[i], "{")
        for j in range(len(struct_content[i])):
            result += "    {}\n".format(struct_content[i][j])
        result += "};\n"
        result += "\n"
    result += "\n"
    return result

def generate_interface():
    result = ""
    result += "/*----------------------------------------------------------------------------------------------------------------------\n"
    result += "Interfaces\n"
    result += "----------------------------------------------------------------------------------------------------------------------*/\n"
    result += "\n"
    for i in range(len(interface_name)):
        result += "/*----------------------------------------------------------------------------------------------------------------------\n"
        #result += "Steinberg::{}\n".format(interface_name[i])
        result += "{} */\n".format(interface_source[i])
        result += "\n"
        result += "typedef struct SMTG_{}Vtbl\n".format(interface_name[i])
        result += "{\n"
        result += generate_methods(i)
        result += "{} SMTG_{}Vtbl;\n".format("}", interface_name[i])
        result += "\n"
        result += "typedef struct SMTG_{}\n".format(interface_name[i])
        result += "{\n"
        result += "    SMTG_{}Vtbl* lpVtbl;\n".format(interface_name[i])
        result += "{} SMTG_{};\n".format("}", interface_name[i])
        result += "\n"
        if interface_name[i] in ID_table:
            interface_ids = ID_table[interface_name[i]]
            result += "/*----------------------------------------------------------------------------------------------------------------------\n"
            result += "SMTG_TUID SMTG_{}_iid = SMTG_INLINE_UID ({}, {}, {}, {});\n".format(interface_name[i],
                                                                                     interface_ids[0],
                                                                                     interface_ids[1],
                                                                                     interface_ids[2],
                                                                                     interface_ids[3])
            result += "----------------------------------------------------------------------------------------------------------------------*/\n"
        result += "\n"
    result += "\n"
    return result

def generate_methods(i):
    result = ""
    methods_location = 0
    for k in range(len(inherits_table[i])):
        if inherits_table[i][k] in interface_name:
            methods_location = interface_name.index(inherits_table[i][k])
        result += "    /* methods derived from \"{}\": */\n".format(inherits_table[i][k])
        for j in range(len(method_name[methods_location])):
            if method_args[methods_location][j][0] == "":
                result += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);\n".format(
                    method_return[methods_location][j],
                    method_name[methods_location][j])
            elif method_args[methods_location][j][0] != "":

                result += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});\n".format(
                    method_return[methods_location][j],
                    method_name[methods_location][j],
                    method_args[methods_location][j][0])
        result += "\n"
    result += "    /* methods defined in \"{}\": */\n".format(interface_name[i])
    for j in range(len(method_name[i])):
        if method_args[i][j][0] == "":
            result += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);\n".format(method_return[i][j],
                                                                                              method_name[i][j])
        elif method_args[i][j][0] != "":
            result += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});\n".format(method_return[i][j],
                                                                                                method_name[i][j],
                                                                                                method_args[i][j][
                                                                                                    0])
    result += "\n"
    return result


def generate_conversion():
    result = generate_standard()
    result += generate_interface_forward()
    result += generate_enums()
    result += generate_structs()
    result += generate_interface()
    return result


def print_info():
    print("Number of enums: {}".format(len(enum_name)))
    for i in range(len(enum_name)):
        if enum_name[i] != "":
            print(" {}".format(enum_name[i]))
    print()
    print("Number of structs: {}".format(len(struct_table)))
    for i in range(len(struct_table)):
        print(" {}".format(struct_table[i]))
    print()
    print("Number of interfaces: {}".format(len(interface_name)))
    print()
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
    brackets = ""
    if "[" in source:
        brackets = source[source.index("["):]
        source = source[:source.index("[")]
    return source, brackets

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
    return [t.spelling for t in i.get_tokens()]


# ----- conversion function --------------------------------------------------------------------------------------------

def convert(source):
    found_const = False
    found_unsigned = False
    found_doubleptr = False
    found_ptr = False
    found_rvr = False
    found_lvr = False
    found_ptr_lvr = False

    source = str(source)
    print(source)

    if "const " in source:
        source = source.replace("const ", "")
        found_const = True
    if "unsigned" in source:
        source = source.replace("unsigned ", "")
        found_unsigned = True
    if "*&" in source:
        source = source.replace(" *&", "")
        found_ptr_lvr = True
    elif "**" in source:
        source = source.replace(" **", "")
        found_doubleptr = True
    elif "*" in source:
        source = source.replace(" *", "")
        found_ptr = True
    elif "&&" in source:
        source = source.replace(" &&", "")
        found_rvr = True
    elif "&" in source:
        source = source.replace(" &", "")
        found_lvr = True
    source, brackets = normalise_args(source)
    source = normalise_namespace(source)
    print("  ", source)

    if source in enum_table_l:
        source = convert(enum_table_r[enum_table_l.index(source)])
    elif source in SMTG_TUID_table:
        source = "SMTG_TUID"
    elif source in struct_table_preparse or source in interface_name_preparse or\
        source in typedef_name_preparse or source in enum_name_preparse:
        source = "SMTG_{}".format(source)
    elif source == "_iid":
        source = "iid"
    elif source in remove_table:
        source = ""

    source = source + brackets

    if found_unsigned:
        source = "unsigned {}".format(source)
    if found_const:
        source = "const {}".format(source)
    if found_doubleptr:
        source = "{}**".format(source)
    if found_ptr:
        source = "{}*".format(source)
    if found_rvr:
        source = "{}&&".format(source)
    if found_lvr:
        source = "{}&".format(source)
    if found_ptr_lvr:
        source = "{}*&".format(source)
    print("     ", source)
    print()
    return source







if __name__ == '__main__':

    print_header = True
    write_header = True


# ----- Establish Translation Unit -----
    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()
    index = Index.create()
    include_path = normalise_link(Path(sys.argv[1]).parents[2])
    tu = index.parse(normalise_link(filename[0]), ['-I', include_path, '-x', 'c++-header'])
    source_file = normalise_link(tu.spelling)

# ----- Arrays -----
    interface_source = []
    interface_description = []
    interface_name = []
    interface_name_preparse = []
    inherits_table = []

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
    enum_name_preparse = []
    enum_table = []
    enum_table_l = []
    enum_table_r = []
    enum_source = []

    typedef_name = []
    typedef_name_preparse = []
    typedef_return = []
    typedef_interface_name = []
    typedef_interface_return = []


    ID_table = {}


# ----- Conversion helper arrays -----
    blacklist = ["FUID", "FReleaser", "SMTG_Item"]
    remove_table = ["/*out*/", "/*in*/"]
    SMTG_TUID_table = ["FIDString", "TUID"]



# ----- Parse -----
    preparse_header(tu.cursor)
    parse_header(tu.cursor)
    header_content = generate_conversion()

# ----- Write -----
    if write_header:
        header_path = "test_header.h"
        with open(header_path, 'w') as f:
            f.write(header_content)

# ----- Print -----
    if print_header:
        print(header_content)
        print_info()
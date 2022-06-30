import sys
from optparse import OptionParser
from pathlib import Path

from clang.cindex import Index, TokenGroup

from clang_helpers import set_library_path


# ----- preparse -------------------------------------------------------------------------------------------------------

def preparse_header(cursor):
    for cursor_child in cursor.get_children():
        if include_path in normalise_link(cursor_child.location.file) and normalise_link(cursor_child.location.file) not in includes_table_preparse:
            includes_table_preparse.append(normalise_link(cursor_child.location.file))
            preparse_namespace(cursor_child)
            preparsing(cursor_child)

def preparse_namespace(cursor):
    if cursor.kind == cursor.kind.NAMESPACE:
        for cursor_child in cursor.get_children():
            preparse_namespace(cursor_child)
            preparsing(cursor_child)

def preparsing(cursor):
    preparse_interfaces(cursor)
    preparse_enum(cursor)
    preparse_structs(cursor)
    parse_typedefs(cursor)


def preparse_interfaces(cursor):
    if cursor.kind == cursor.kind.CLASS_DECL:
        interface_name_preparse.append(normalise_namespace(cursor.spelling))
        for cursor_child in cursor.get_children():
            #parse_typedefs(cursor_child)
            preparse_enum(cursor_child)

def preparse_enum(cursor):
    if cursor.kind == cursor.kind.ENUM_DECL:
        enum_name_preparse.append(cursor.spelling)

def preparse_structs(cursor):
    if cursor.kind == cursor.kind.STRUCT_DECL:
        r = 0
        for cursor_child in cursor.get_children():
            preparse_enum(cursor_child)
            if cursor_child.kind == cursor_child.kind.FIELD_DECL:
                if r == 0:
                    struct_table_preparse.append(cursor.spelling)
                r = r + 1

def parse_typedefs(cursor):
    if cursor.kind == cursor.kind.TYPEDEF_DECL:
        if cursor.spelling not in SMTG_TUID_table:
            typedef_name_preparse.append(cursor.spelling)

        if cursor.underlying_typedef_type.kind == cursor.type.kind.CONSTANTARRAY:
            typedef_return.append(convert(cursor.underlying_typedef_type.element_type.spelling))
            typedef_name.append("{}[{}]".format(convert(cursor.spelling), cursor.underlying_typedef_type.element_count))
        else:
            typedef_return.append(convert(cursor.underlying_typedef_type.spelling))
            typedef_name.append(convert(cursor.spelling))


# ----- parse ----------------------------------------------------------------------------------------------------------

def parse_header(cursor):
    for cursor_child in cursor.get_children():
        if include_path in normalise_link(cursor_child.location.file) and normalise_link(cursor_child.location.file) not in includes_table:
            includes_table.append(normalise_link(cursor_child.location.file))
            parse_namespace(cursor_child)
            parsing(cursor_child)

def parse_namespace(cursor):
        if cursor.kind == cursor.kind.NAMESPACE:
            for cursor_child in cursor.get_children():
                parse_namespace(cursor_child)
                parsing(cursor_child)

def parsing(cursor):
    parse_interfaces(cursor)
    parse_enum(cursor)
    parse_structs(cursor)
    parse_IID(cursor)

def parse_IID(cursor):
    if cursor.kind == cursor.kind.VAR_DECL and cursor.spelling.endswith("_iid"):
        ID_tokens = get_tokens_from_extent(cursor)
        ID_table[ID_tokens[2]] = [ID_tokens[4], ID_tokens[6], ID_tokens[8], ID_tokens[10]]

def get_tokens_from_extent(cursor):
    tu = cursor.translation_unit
    extent = tu.get_extent(cursor.location.file.name, [cursor.extent.start.offset, cursor.extent.end.offset])
    return [token.spelling for token in TokenGroup.get_tokens(tu, extent)]

# ----- parse interfaces ---------------------------------------------------------------

def parse_interfaces(cursor):
    if cursor.kind == cursor.kind.CLASS_DECL and cursor.spelling not in blacklist:
        children = list(cursor.get_children())
        if not children:
            return
        interface_source.append("Source: \"{}\", line {}".format(normalise_link(cursor.location.file), cursor.location.line))
        interface_description.append(cursor.brief_comment)
        interface_name.append(normalise_namespace(cursor.spelling))
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
        for cursor_child in children:
            parse_enum(cursor_child)
            parse_inheritance(cursor_child)
            method_count_local = parse_methods(cursor_child, method_count_local, interface_name[-1])


# ----- parse inheritances ---------------------------------------------------------------

def parse_inheritance(cursor):
    if cursor.kind == cursor.kind.CXX_BASE_SPECIFIER:
        position = len(interface_name) - 1
        for k in range(len(inherits_table[position]) + 1):
            if normalise_namespace(cursor.type.spelling) in interface_name:
                inherits_location = interface_name.index(normalise_namespace(cursor.type.spelling))
                for n in range(len(inherits_table[inherits_location])):
                    inherits_table[position].append(inherits_table[inherits_location][n])
        inherits_table[position].append(normalise_namespace(cursor.type.spelling))


# ----- parse methods ---------------------------------------------------------------

def parse_methods(cursor, method_count_local, current_interface):
    if cursor.kind == cursor.kind.CXX_METHOD:
        method_count_local = method_count_local + 1
        position = len(interface_name) - 1

        method_args[position].append("")
        method_args[position][method_count_local - 1] = []

        method_name[position].append(cursor.spelling)

        method_return[position].append(convert(get_underlying_type(cursor.result_type, current_interface)))
        method_args_content = parse_method_arguments(cursor, current_interface)
        method_args[position][method_count_local - 1].append("".join(method_args_content))
    return method_count_local

def get_namespaces(source):
    if "const " in source:
        source = source.replace("const ", "")
    return source.split("::")[:-1]


def parse_method_arguments(cursor, current_interface):
    p = 0
    method_args_content = []
    for cursor_child in cursor.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        method_args_content.append(convert(get_underlying_type(cursor_child.type, current_interface)))
        method_args_content.append(" ")
        method_args_content.append(convert(cursor_child.spelling))
        p = p + 1
    return method_args_content

def get_underlying_type(type, current_interface):
    if type.kind == type.kind.ENUM:
        return type.spelling
    namespaces = get_namespaces(type.spelling)
    if not namespaces or namespaces[-1] != current_interface:
        return type.spelling
    result_type = type
    while result_type.get_pointee().kind != type.kind.INVALID:
        result_type = result_type.get_pointee()
    suffix = type.spelling[len(result_type.spelling):]
    suffix = suffix.replace('*const', '* const')
    result_type = result_type.get_declaration().underlying_typedef_type
    return result_type.spelling + suffix


# ----- parse structs ---------------------------------------------------------------

def parse_structs(cursor):
    if cursor.kind == cursor.kind.STRUCT_DECL and cursor.spelling not in blacklist:
        r = 0
        position = len(struct_table) - 1
        for cursor_child in cursor.get_children():
            parse_enum(cursor_child)
            if cursor_child.kind == cursor_child.kind.FIELD_DECL:
                struct_args = ""

                if r == 0:
                    struct_table.append(cursor.spelling)
                    position = len(struct_table) - 1
                    struct_source.append("Source: \"{}\", line {}".format(normalise_link(cursor.location.file), cursor.location.line))
                    struct_content.append("")
                    struct_content[position] = []
                if cursor_child.type.kind == cursor_child.type.kind.CONSTANTARRAY:
                    struct_return = convert(cursor_child.type.element_type.spelling)
                else:
                    struct_return = convert(cursor_child.type.spelling)

                for cursor_child_child in cursor_child.get_children():
                    if cursor_child_child.kind == cursor_child_child.kind.DECL_REF_EXPR:
                        struct_args = convert(cursor_child_child.spelling)

                if struct_args != "":
                    struct_content[position].append(
                        "{} {} [{}];".format(struct_return, cursor_child.spelling, struct_args))
                else:
                    struct_content[position].append("{} {};".format(struct_return, cursor_child.spelling))

                r = r + 1


# ----- parse enums ---------------------------------------------------------------

def parse_enum(cursor):
    if cursor.kind == cursor.kind.ENUM_DECL:
        enum_name.append(cursor.spelling)
        position = len(enum_name) - 1
        enum_table.append("")
        enum_table[position] = []
        enum_source.append("Source: {}, line {}".format(normalise_link(cursor.location.file), cursor.location.line))

        for cursor_child in cursor.get_children():
            if cursor_child.kind == cursor_child.kind.ENUM_CONSTANT_DECL:
                enum_table[position].append(cursor_child.spelling)
                enum_table_l.append(cursor_child.spelling)
                parse_enum_value(cursor_child)

def parse_enum_value(cursor):
    children = False
    position = len(enum_name) - 1
    for cursor_child in cursor.get_children():
        children = True
        if cursor_child.kind == cursor_child.kind.INTEGER_LITERAL or cursor_child.kind == cursor_child.kind.BINARY_OPERATOR:
            if array_to_string(get_values_in_extent(cursor_child), True) != "":
                enum_table[position].append(array_to_string(get_values_in_extent(cursor_child), True))
                enum_table_r.append(array_to_string(get_values_in_extent(cursor_child), True))
        elif cursor_child.kind == cursor_child.kind.UNEXPOSED_EXPR:
            parse_enum_value(cursor_child)
        else:
            enum_table[position].append("nil")
            enum_table_r.append("nil")
    if children == False:
        enum_table[position].append("nil")
        enum_table_r.append("nil")


# ----- output to string ------------------------------------------------------------------------------------------------

def generate_standard():
    string = "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Source file: {}\n".format(source_file)
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    string += "#include <stdint.h>\n"
    string += "\n"
    string += "#define SMTG_STDMETHODCALLTYPE\n"
    string += "\n"
    string += "#if _WIN32 /* COM_COMPATIBLE */\n"
    string += "#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n"
    string += "{ \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0x000000FF)      ), (SMTG_int8)(((SMTG_uint32)(l1) & 0x0000FF00) >>  8), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0x00FF0000) >> 16), (SMTG_int8)(((SMTG_uint32)(l1) & 0xFF000000) >> 24), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0x00FF0000) >> 16), (SMTG_int8)(((SMTG_uint32)(l2) & 0xFF000000) >> 24), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0x000000FF)      ), (SMTG_int8)(((SMTG_uint32)(l2) & 0x0000FF00) >>  8), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l3) & 0x00FF0000) >> 16), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l3) & 0x000000FF)      ), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l4) & 0x00FF0000) >> 16), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l4) & 0x000000FF)      )  \\\n"
    string += "}\n"
    string += "#else\n"
    string += "#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n"
    string += "{ \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l1) & 0x00FF0000) >> 16), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l1) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l1) & 0x000000FF)      ), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l2) & 0x00FF0000) >> 16), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l2) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l2) & 0x000000FF)      ), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l3) & 0x00FF0000) >> 16), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l3) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l3) & 0x000000FF)      ), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0xFF000000) >> 24), (SMTG_int8)(((SMTG_uint32)(l4) & 0x00FF0000) >> 16), \\\n"
    string += "	(SMTG_int8)(((SMTG_uint32)(l4) & 0x0000FF00) >>  8), (SMTG_int8)(((SMTG_uint32)(l4) & 0x000000FF)      )  \\\n"
    string += "}\n"
    string += "#endif\n"
    string += "\n"
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Typedefs\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    string += generate_typedefs()
    string += "\n"
    string += "\n"
    return string

def generate_typedefs():
    string = ""
    for i in range(len(typedef_name)):
        if typedef_return[i] != []:
            string += "typedef {} {};\n".format(typedef_return[i], typedef_name[i])
    return string

def generate_forward():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Interface forward declarations\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(interface_name)):
        string += "struct {};\n".format(convert(interface_name[i]))
    string += "\n"
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Struct forward declarations\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(struct_table)):
        string += "struct {};\n".format(convert(struct_table[i]))
    string += "\n"
    string += "\n"
    return string

def generate_enums():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Enums\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(enum_table)):
        if enum_name[i] == "":
            continue
        string += "/*----------------------------------------------------------------------------------------------------------------------\n"
        string += "{} */\n".format(enum_source[i])
        string += "\n"
        string += "enum SMTG_{}\n".format(enum_name[i])
        string += "{\n"
        for j in range(int(len(enum_table[i]) / 2)):
            if j < int(len(enum_table[i]) / 2) - 1:
                if enum_table[i][2 * j + 1] != "nil":
                    string += "{} = {},\n".format(enum_table[i][2 * j], enum_table[i][2 * j + 1])
                else:
                    string += "{},\n".format(enum_table[i][2 * j])
            else:
                if enum_table[i][2 * j + 1] != "nil":
                    string += "{} = {}\n".format(enum_table[i][2 * j], enum_table[i][2 * j + 1])
                else:
                    string += "{}\n".format(enum_table[i][2 * j])
        string += "};\n"
        string += "\n"
    string += "\n"
    return string

def generate_structs():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Structs\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(struct_table)):
        string += "/*----------------------------------------------------------------------------------------------------------------------\n"
        string += "{} */\n".format(struct_source[i])
        string += "\n"
        string += "struct SMTG_{} {}\n".format(struct_table[i], "{")
        for j in range(len(struct_content[i])):
            string += "    {}\n".format(struct_content[i][j])
        string += "};\n"
        string += "\n"
    string += "\n"
    return string

def generate_interface():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Interfaces\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(interface_name)):
        string += "/*----------------------------------------------------------------------------------------------------------------------\n"
        #string += "Steinberg::{}\n".format(interface_name[i])
        string += "{} */\n".format(interface_source[i])
        string += "\n"
        string += "typedef struct SMTG_{}Vtbl\n".format(interface_name[i])
        string += "{\n"
        string += generate_methods(i)
        string += "{} SMTG_{}Vtbl;\n".format("}", interface_name[i])
        string += "\n"
        string += "typedef struct SMTG_{}\n".format(interface_name[i])
        string += "{\n"
        string += "    SMTG_{}Vtbl* lpVtbl;\n".format(interface_name[i])
        string += "{} SMTG_{};\n".format("}", interface_name[i])
        string += "\n"
        if interface_name[i] in ID_table:
            interface_ids = ID_table[interface_name[i]]
            #string += "/*----------------------------------------------------------------------------------------------------------------------\n"
            string += "SMTG_TUID SMTG_{}_iid = SMTG_INLINE_UID ({}, {}, {}, {});\n".format(interface_name[i],
                                                                                     interface_ids[0],
                                                                                     interface_ids[1],
                                                                                     interface_ids[2],
                                                                                     interface_ids[3])
            #string += "----------------------------------------------------------------------------------------------------------------------*/\n"
        string += "\n"
    string += "\n"
    return string

def generate_methods(i):
    string = ""
    methods_location = 0
    for k in range(len(inherits_table[i])):
        if inherits_table[i][k] in interface_name:
            methods_location = interface_name.index(inherits_table[i][k])
        string += "    /* methods derived from \"{}\": */\n".format(inherits_table[i][k])
        for j in range(len(method_name[methods_location])):
            if method_args[methods_location][j][0] == "":
                string += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);\n".format(
                    method_return[methods_location][j],
                    method_name[methods_location][j])
            elif method_args[methods_location][j][0] != "":

                string += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});\n".format(
                    method_return[methods_location][j],
                    method_name[methods_location][j],
                    method_args[methods_location][j][0])
        string += "\n"
    string += "    /* methods defined in \"{}\": */\n".format(interface_name[i])
    for j in range(len(method_name[i])):
        if method_args[i][j][0] == "":
            string += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface);\n".format(method_return[i][j],
                                                                                              method_name[i][j])
        elif method_args[i][j][0] != "":
            string += "    {} (SMTG_STDMETHODCALLTYPE* {}) (void* thisInterface, {});\n".format(method_return[i][j],
                                                                                                method_name[i][j],
                                                                                                method_args[i][j][
                                                                                                    0])
    string += "\n"
    return string

def generate_conversion():
    string = generate_standard()
    string += generate_forward()
    string += generate_enums()
    string += generate_structs()
    string += generate_interface()
    return string


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

def normalise_brackets(source):
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
    #print(source)

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
    source, brackets = normalise_brackets(source)
    source = normalise_namespace(source)
    #print("  ", source)

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
    #print("     ", source)
    #print()
    return source







if __name__ == '__main__':

    print_header = True
    write_header = True


# ----- Establish Translation Unit -----
    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()
    if not filename:
        print ('No filename was specified!')
        exit(1)
    set_library_path()
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
    blacklist = ["FUID", "FReleaser"]
    remove_table = ["/*out*/", "/*in*/"]
    SMTG_TUID_table = ["FIDString", "TUID"]

# ----- Parse -----
    preparse_header(tu.cursor)
    parse_header(tu.cursor)
    header_content = generate_conversion()

# ----- Write -----
    if write_header:
        header_path = "test_header.h"
        with open(header_path, 'w') as h:
            h.write(header_content)

# ----- Print -----
    if print_header:
        print(header_content)
        print_info()
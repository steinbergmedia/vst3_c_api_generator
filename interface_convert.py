import sys
from optparse import OptionParser
from pathlib import Path
from typing import List

from clang.cindex import Index, TokenGroup, SourceLocation, Cursor, Token, Type

from clang_helpers import set_library_path


# ----- parse ----------------------------------------------------------------------------------------------------------

def parse_header(cursor):
    for cursor_child in cursor.get_children():
        cursor_child_location = normalise_link(cursor_child.location.file.name)
        if not cursor_child_location.startswith(include_path) or cursor_child_location in includes_table:
            continue
        includes_table.append(cursor_child_location)
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
    store_typedefs(cursor)
    parse_variables(cursor)

def parse_IID(cursor):
    if cursor.kind == cursor.kind.VAR_DECL and cursor.spelling.endswith("_iid"):
        ID_tokens = get_tokens_from_extent(cursor)
        ID_table[ID_tokens[2]] = [ID_tokens[4], ID_tokens[6], ID_tokens[8], ID_tokens[10]]

def get_tokens_from_extent(cursor):
    tu = cursor.translation_unit
    extent = tu.get_extent(cursor.location.file.name, [cursor.extent.start.offset, cursor.extent.end.offset])
    return [token.spelling for token in TokenGroup.get_tokens(tu, extent)]


# ----- parse typedefs ---------------------------------------------------------------

def store_typedefs(cursor):
    return_type, name = parse_typedefs(cursor)
    if return_type and name:
        typedef_return.append(return_type)
        typedef_name.append(name)


def store_interface_typedefs(cursor):
    return_type, name = parse_typedefs(cursor)
    if return_type and name:
        interface_typedef_return.append(return_type)
        interface_typedef_name.append(name)


def parse_typedefs(cursor):
    if cursor.kind != cursor.kind.TYPEDEF_DECL and cursor.kind != cursor.kind.TYPE_ALIAS_DECL:
        return None, None
    if cursor.underlying_typedef_type.kind == cursor.type.kind.CONSTANTARRAY:
        return_type = convert(cursor.underlying_typedef_type.element_type)
        name = "{}[{}]".format(convert(cursor.type), cursor.underlying_typedef_type.element_count)
    else:
        return_type = convert(cursor.underlying_typedef_type)
        name = convert(cursor)
    return return_type, name

# ----- parse interfaces ---------------------------------------------------------------

def parse_interfaces(cursor):
    if cursor.kind == cursor.kind.CLASS_DECL and cursor.spelling not in blacklist:
        children = list(cursor.get_children())
        if not children:
            return
        interface_source.append(convert_cursor_location(cursor.location))
        interface_description.append(cursor.brief_comment)
        interface_name.append(convert(cursor))
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
            store_interface_typedefs(cursor_child)
            parse_enum(cursor_child)
            parse_inheritance(cursor_child)
            parse_variables(cursor_child)
            method_count_local = parse_methods(cursor_child, method_count_local, interface_name[-1])


# ----- parse inheritances ---------------------------------------------------------------

def parse_inheritance(cursor):
    if cursor.kind == cursor.kind.CXX_BASE_SPECIFIER:
        position = len(interface_name) - 1
        for k in range(len(inherits_table[position]) + 1):
            if convert_namespace(cursor.type.spelling) in interface_name:
                inherits_location = interface_name.index(convert_namespace(cursor.type.spelling))
                for n in range(len(inherits_table[inherits_location])):
                    inherits_table[position].append(inherits_table[inherits_location][n])
        inherits_table[position].append(convert_namespace(cursor.type.spelling))


# ----- parse methods ---------------------------------------------------------------

def parse_methods(cursor, method_count_local, current_interface):
    if cursor.kind == cursor.kind.CXX_METHOD:
        method_count_local = method_count_local + 1
        position = len(interface_name) - 1

        method_args[position].append("")
        method_args[position][method_count_local - 1] = []

        method_name[position].append(cursor.spelling)

        method_return[position].append(convert(cursor.result_type))
        method_args_content = parse_method_arguments(cursor, current_interface)
        method_args[position][method_count_local - 1].append("".join(method_args_content))
    return method_count_local

def parse_method_arguments(cursor, current_interface):
    p = 0
    method_args_content = []
    for cursor_child in cursor.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        method_args_content.append(convert(cursor_child.type))
        method_args_content.append(" ")
        method_args_content.append(convert_method_args_name(cursor_child.spelling))
        p = p + 1
    return method_args_content


# ----- parse variables ---------------------------------------------------------------


def parse_variables(cursor):
    if cursor.kind == cursor.kind.VAR_DECL and cursor.type.kind == cursor.type.kind.TYPEDEF:
        variable_return.append(convert(cursor.type))
        namespace_prefix = create_namespace_prefix(cursor)
        variable_name.append("{}{}".format(namespace_prefix, convert(cursor)))
        last_cursor_child = list(cursor.get_children())[-1]
        grand_children = list(last_cursor_child.get_children())
        if len(grand_children) == 1 and grand_children[0].kind == cursor.kind.STRING_LITERAL:
            # Expand only macros with single string literals
            variable_value.append(grand_children[0].spelling)
        else:
            value = tokens_to_string(list(last_cursor_child.get_tokens()))
            variable_value.append(value)

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
                    struct_table.append(convert(cursor))
                    position = len(struct_table) - 1
                    struct_source.append(convert_cursor_location(cursor.location))
                    struct_content.append("")
                    struct_content[position] = []
                if cursor_child.type.kind == cursor_child.type.kind.CONSTANTARRAY:
                    struct_return = convert(cursor_child.type.element_type)
                else:
                    struct_return = convert(cursor_child.type)

                for cursor_child_child in cursor_child.get_children():
                    if cursor_child_child.kind == cursor_child_child.kind.DECL_REF_EXPR:
                        struct_args = convert(cursor_child_child)

                if struct_args != "":
                    struct_content[position].append(
                        "{} {}[{}];".format(struct_return, cursor_child.spelling, struct_args))
                else:
                    struct_content[position].append("{} {};".format(struct_return, cursor_child.spelling))

                r = r + 1


# ----- parse enums ---------------------------------------------------------------

def parse_enum(cursor):
    if cursor.kind == cursor.kind.ENUM_DECL:
        namespace_prefix = create_namespace_prefix(cursor)
        if cursor.spelling == "":
            enum_name.append(cursor.spelling)
        else:
            enum_name.append("{}{}".format(namespace_prefix, convert(cursor)))
        position = len(enum_name) - 1
        enum_table.append("")
        enum_table[position] = []
        enum_source.append(convert_cursor_location(cursor.location))
        for cursor_child in cursor.get_children():
            if cursor_child.kind == cursor_child.kind.ENUM_CONSTANT_DECL:
                namespace_prefix = create_namespace_prefix(cursor_child)
                enum_table[position].append("{}{}".format(namespace_prefix, cursor_child.spelling))
                enum_table_l.append(cursor_child.spelling)
                parse_enum_value(cursor_child)

def parse_enum_value(cursor):
    children = False
    position = len(enum_name) - 1
    for cursor_child in cursor.get_children():
        children = True
        is_negative = cursor_child.kind == cursor_child.kind.UNARY_OPERATOR
        if cursor_child.kind == cursor_child.kind.INTEGER_LITERAL or cursor_child.kind == cursor_child.kind.BINARY_OPERATOR or is_negative:
            if array_to_string(get_values_in_extent(cursor_child), True) != "":
                values = get_values_in_extent(cursor_child)
                tokens = list(cursor_child.get_tokens())
                for i in range(len(tokens)):
                    if values[i] in enum_table_l:
                        namespace_prefix = create_namespace_prefix(tokens[i].cursor)
                        values[i] = "{}{}".format(namespace_prefix, values[i])
                enum_table[position].append(array_to_string(values, not is_negative))
                enum_table_r.append(array_to_string(values, True))
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
            if typedef_return[i] != []:
                if typedef_return[i] in struct_table or typedef_return[i] in interface_name \
                        or typedef_return[i] in enum_name or typedef_return[i] in typedef_name:
                    string += "typedef struct {} {};\n".format(typedef_return[i], typedef_name[i])
                else:
                    string += "typedef {} {};\n".format(typedef_return[i], typedef_name[i])
    return string

def generate_interface_typedefs():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Interface typedefs\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(interface_typedef_name)):
        if typedef_return[i] != []:
            if interface_typedef_return[i] in struct_table or interface_typedef_return[i] in interface_name\
                    or interface_typedef_return[i] in enum_name or interface_typedef_return[i] in typedef_name:
                string += "typedef struct {} {};\n".format(interface_typedef_return[i], interface_typedef_name[i])
            else:
                string += "typedef {} {};\n".format(interface_typedef_return[i], interface_typedef_name[i])
    string += "\n"
    string += "\n"
    return string

def generate_forward():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Interface forward declarations\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(interface_name)):
        string += "struct {};\n".format(interface_name[i])
    string += "\n"
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Struct forward declarations\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(struct_table)):
        string += "struct {};\n".format(struct_table[i])
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
        string += "enum {}\n".format(enum_name[i])
        string += "{\n"
        enum_count = int(len(enum_table[i]) / 2)
        for j in range(enum_count):
            if enum_table[i][2 * j + 1] != "nil":
                string += "{} = {}".format(enum_table[i][2 * j], enum_table[i][2 * j + 1])
            else:
                string += "{}".format(enum_table[i][2 * j])

            if j < enum_count - 1:
                string += ","
            string += "\n"



        string += "};\n"
        string += "\n"
    string += "\n"
    return string


def get_converted_namespaces(source):
    if "const " in source:
        source = source.replace("const ", "")
    return source.split("_")[:-1]

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
        string += "struct {} {}\n".format(struct_table[i], "{")
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
        string += "{} */\n".format(interface_source[i])
        string += "\n"
        string += "typedef struct {}Vtbl\n".format(interface_name[i])
        string += "{\n"
        string += generate_methods(i)
        string += "{} {}Vtbl;\n".format("}", interface_name[i])
        string += "\n"
        string += "typedef struct {}\n".format(interface_name[i])
        string += "{\n"
        string += "    {}Vtbl* lpVtbl;\n".format(interface_name[i])
        string += "{} {};\n".format("}", interface_name[i])
        string += "\n"
        if interface_name[i] in ID_table:
            interface_ids = ID_table[interface_name[i]]
            string += "Steinberg_TUID {}_iid = SMTG_INLINE_UID ({}, {}, {}, {});\n".format(interface_name[i],
                                                                                     interface_ids[0],
                                                                                     interface_ids[1],
                                                                                     interface_ids[2],
                                                                                     interface_ids[3])
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

def generate_variables():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "Variable declarations\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for i in range(len(variable_name)):
        string +=("{} {} = {};\n".format(variable_return[i], variable_name[i], variable_value[i]))
    string += "\n"
    string += "\n"
    return string

def generate_conversion():
    string = generate_standard()
    string += generate_forward()
    string += generate_interface_typedefs()
    string += generate_variables()
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


def normalise_link(source: str) -> str:
    return source.replace('\\', '/')


def convert_cursor_location(cursor_location: SourceLocation) -> str:
    return 'Source: "{}", line {}'.format(normalise_link(cursor_location.file.name), cursor_location.line)


def convert_namespace(source: str) -> str:
    return source.replace('::', '_')


def array_to_string(array: List, insert_spaces: bool) -> str:
    divider = ''
    if insert_spaces:
        divider = ' '
    return divider.join(array)


def tokens_to_string(tokens: List[Token]) -> str:
    result = ''
    previous_kind = None

    for token in tokens:
        if token.spelling == "::":
            continue
        cursor = token.cursor
        namespace_prefix = ""
        if cursor.kind == cursor.kind.DECL_REF_EXPR or cursor.kind == cursor.kind.TYPE_REF:
            namespace_prefix = create_namespace_prefix(cursor)
        if token.spelling == '(' and previous_kind == cursor.kind.TYPE_REF:
            # e.g.: uint64 (0xffffffff)
            result += ' '
        if token.spelling == ')':
            # insert space after closing bracket, if not followed by another one
            if result and result[-1] == ')':
                result.strip()
            result += f'{namespace_prefix}{token.spelling} '
        elif cursor.kind == cursor.kind.BINARY_OPERATOR:
            # surround binary operators with spaces
            result = result.strip()
            result += f' {token.spelling} '
        else:
            result += namespace_prefix + token.spelling
        previous_kind = cursor.kind
    result = result.strip()
    return result


def remove_namespaces(string: str) -> str:
    if '::' not in string:
        return string
    return string[string.rindex('::') + 2:]


def create_namespace_prefix(cursor: Cursor) -> str:
    namespaces = get_namespaces(cursor)
    if not namespaces:
        return ''
    return '_'.join(namespaces) + '_'


def get_namespaces(cursor: Cursor) -> List[str]:
    cursor_definition = cursor.get_definition()
    if cursor_definition:
        cursor = cursor_definition
    cursor = cursor.lexical_parent
    namespaces = []
    while cursor and cursor.kind != cursor.kind.TRANSLATION_UNIT:
        if cursor.spelling:
            namespaces.append(cursor.spelling)
        cursor = cursor.lexical_parent
    namespaces.reverse()
    return namespaces


def get_values_in_extent(cursor: Cursor) -> List[str]:
    return [token.spelling for token in cursor.get_tokens()]


def get_definition_tokens(cursor: Cursor) -> List[Token]:
    result = []
    equal_sign_found = False
    for token in cursor.get_definition().get_tokens():
        if token.spelling == '=':
            equal_sign_found = True
            continue
        if not equal_sign_found:
            continue
        if token.kind == token.kind.PUNCTUATION or token.kind == token.kind.LITERAL:
            result.append(token)
        else:
            result += get_definition_tokens(token.cursor)
    return result


def replace_enum_value(cursor: Cursor) -> str:
    return tokens_to_string(get_definition_tokens(cursor))


def convert_method_args_name(source: str) -> str:
    if source == '_iid':
        return 'iid'
    return source


# ----- conversion function --------------------------------------------------------------------------------------------


def convert(source):
    found_const = False
    found_const_end = False
    found_unsigned = False
    found_doubleptr = False
    found_ptr = False
    found_lvr = False
    found_ptr_lvr = False
    namespace_prefix = ""
    if type(source) == Cursor:
        namespace_prefix = create_namespace_prefix(source)
        string = source.spelling
    elif type(source) == Type:
        string = convert_namespace(source.spelling)
    elif type(source) == str:
        string = source
    else:
        raise(TypeError("Source is neither cursor nor type"))
    #print(string)
    if "const " in string:
        string = string.replace("const ", "")
        found_const = True
    if string.endswith("const"):
        string = string.replace("const", "")
        found_const_end = True
    if "unsigned" in string:
        string = string.replace("unsigned ", "")
        found_unsigned = True
    if "*&" in string:
        string = string.replace(" *&", "")
        found_ptr_lvr = True
    elif "**" in string:
        string = string.replace(" **", "")
        found_doubleptr = True
    elif "*" in string:
        string = string.replace(" *", "")
        found_ptr = True
    elif "&" in string:
        string = string.replace(" &", "")
        found_lvr = True
    string = remove_namespaces(string)
    #print("  ", string)

    if string in enum_table_l:
        string = replace_enum_value(source)
    elif string in remove_table:
        string = ""
    else:
        string = ("{}{}".format(namespace_prefix, string))

    if found_unsigned:
        string = "unsigned {}".format(string)
    if found_const:
        string = "const {}".format(string)
    if found_doubleptr:
        string = "{}**".format(string)
    if found_ptr:
        string = "{}*".format(string)
    if found_lvr:
        string = "{}*".format(string)
    if found_ptr_lvr:
        string = "{}**".format(string)
    if found_const_end:
        string = "{} const".format(string)
    #print("     ", string)
    #print()
    return string


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
    include_path = normalise_link(str(Path(sys.argv[1]).parents[2]))
    tu = index.parse(normalise_link(filename[0]), ['-I', include_path, '-x', 'c++-header'])
    source_file = normalise_link(tu.spelling)

# ----- Arrays -----
    interface_source = []
    interface_description = []
    interface_name = []
    inherits_table = []

    includes_list = []
    includes_table = []

    method_name = []
    method_return = []
    method_args = []

    struct_table = []
    struct_content = []
    struct_source = []

    enum_name = []
    enum_table = []
    enum_table_l = []
    enum_table_r = []
    enum_source = []

    typedef_name = []
    typedef_return = []
    typedef_interface_name = []
    typedef_interface_return = []
    interface_typedef_return = []
    interface_typedef_name = []

    variable_return = []
    variable_name = []
    variable_value = []


    ID_table = {}


# ----- Conversion helper arrays -----
    blacklist = ["FUID", "FReleaser"]
    remove_table = ["/*out*/", "/*in*/"]

# ----- Parse -----
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

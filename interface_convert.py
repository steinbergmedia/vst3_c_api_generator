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
        return_type = convert_type(cursor.underlying_typedef_type.element_type)
        name = "{}[{}]".format(convert_type(cursor.type), cursor.underlying_typedef_type.element_count)
    else:
        return_type = convert_type(cursor.underlying_typedef_type)
        name = convert_cursor(cursor)
    return return_type, name

# ----- parse interfaces ---------------------------------------------------------------

def parse_interfaces(cursor):
    if cursor.kind == cursor.kind.CLASS_DECL and cursor.spelling not in blacklist:
        children = list(cursor.get_children())
        if not children:
            return
        interface_source.append(convert_cursor_location(cursor.location))
        interface_description.append(cursor.brief_comment)
        interface_name.append(convert_cursor(cursor))
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

        method_return[position].append(create_struct_prefix(cursor.result_type) + convert_type(cursor.result_type))
        method_args_content = parse_method_arguments(cursor, current_interface)
        method_args[position][method_count_local - 1].append("".join(method_args_content))
    return method_count_local

def parse_method_arguments(cursor, current_interface):
    p = 0
    method_args_content = []
    for cursor_child in cursor.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        method_args_content.append(create_struct_prefix(cursor_child.type) + convert_type(cursor_child.type))
        method_args_content.append(" ")
        method_args_content.append(convert_method_args_name(cursor_child.spelling))
        p = p + 1
    return method_args_content


# ----- parse variables ---------------------------------------------------------------


def parse_variables(cursor):
    if cursor.kind == cursor.kind.VAR_DECL and cursor.type.kind == cursor.type.kind.TYPEDEF:
        variable_return.append(convert_type(cursor.type))
        variable_name.append(convert_cursor(cursor))
        last_cursor_child = list(cursor.get_children())[-1]
        grand_children = list(last_cursor_child.get_children())
        if len(grand_children) == 1:
            if grand_children[0].kind == cursor.kind.STRING_LITERAL:
                # Expand only macros with single string literals
                variable_value.append(grand_children[0].spelling)
            else:
                variable_value.append(replace_expression(grand_children[0], use_definition=True))
        else:
            variable_value.append(replace_expression(last_cursor_child, use_definition=True))

# ----- parse structs ---------------------------------------------------------------


def parse_structs(cursor):
    if cursor.kind == cursor.kind.STRUCT_DECL and cursor.spelling not in blacklist:
        r = False
        position = len(struct_table) - 1
        for cursor_child in cursor.get_children():
            parse_enum(cursor_child)

            if cursor_child.kind == cursor_child.kind.FIELD_DECL:
                struct_args = ""

                if not r:
                    struct_table.append(convert_cursor(cursor))
                    position = len(struct_table) - 1
                    struct_source.append(convert_cursor_location(cursor.location))
                    struct_content.append("")
                    struct_content[position] = []

                if cursor_child.type.kind == cursor_child.type.kind.CONSTANTARRAY:
                    cursor_child_type = cursor_child.type.element_type
                    struct_return = convert_type(cursor_child_type)
                    cursor_child_child = list(cursor_child.get_children())[-1]
                    struct_args = replace_expression(cursor_child_child, use_definition=True)
                else:
                    cursor_child_type = cursor_child.type
                    struct_return = convert_type(cursor_child_type)
                struct_return = create_struct_prefix(cursor_child_type) + struct_return


                #for cursor_child_child in cursor_child.get_children():
                #    if cursor_child_child.kind == cursor_child_child.kind.DECL_REF_EXPR:
                #        struct_args = replace_expression(cursor_child_child, use_definition=True)

                if struct_args != "":
                    struct_content[position].append(
                        "{} {}[{}];".format(struct_return, cursor_child.spelling, struct_args))
                else:
                    struct_content[position].append("{} {};".format(struct_return, cursor_child.spelling))

                r = True


# ----- parse enums ---------------------------------------------------------------


def parse_enum(cursor: Cursor):
    if cursor.kind != cursor.kind.ENUM_DECL:
        return
    if cursor.spelling:
        enum_name.append(create_namespace_prefix(cursor) + cursor.spelling)
    else:
        enum_name.append('')
    enum_source.append(convert_cursor_location(cursor.location))
    enum_definitions = []
    for cursor_child in cursor.get_children():
        if cursor_child.kind != cursor_child.kind.ENUM_CONSTANT_DECL:
            continue
        enum_definitions.append(create_namespace_prefix(cursor_child) + cursor_child.spelling)
        enum_definitions.append(replace_expression(cursor_child))
    enum_table.append(enum_definitions)


# ----- output to string ---------------------------------------------------------------

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
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l1) & 0x000000FF)      ), (Steinberg_int8)(((Steinberg_uint32)(l1) & 0x0000FF00) >>  8), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l1) & 0x00FF0000) >> 16), (Steinberg_int8)(((Steinberg_uint32)(l1) & 0xFF000000) >> 24), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l2) & 0x00FF0000) >> 16), (Steinberg_int8)(((Steinberg_uint32)(l2) & 0xFF000000) >> 24), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l2) & 0x000000FF)      ), (Steinberg_int8)(((Steinberg_uint32)(l2) & 0x0000FF00) >>  8), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l3) & 0xFF000000) >> 24), (Steinberg_int8)(((Steinberg_uint32)(l3) & 0x00FF0000) >> 16), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l3) & 0x0000FF00) >>  8), (Steinberg_int8)(((Steinberg_uint32)(l3) & 0x000000FF)      ), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l4) & 0xFF000000) >> 24), (Steinberg_int8)(((Steinberg_uint32)(l4) & 0x00FF0000) >> 16), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l4) & 0x0000FF00) >>  8), (Steinberg_int8)(((Steinberg_uint32)(l4) & 0x000000FF)      )  \\\n"
    string += "}\n"
    string += "#else\n"
    string += "#define SMTG_INLINE_UID(l1, l2, l3, l4) \\\n"
    string += "{ \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l1) & 0xFF000000) >> 24), (Steinberg_int8)(((Steinberg_uint32)(l1) & 0x00FF0000) >> 16), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l1) & 0x0000FF00) >>  8), (Steinberg_int8)(((Steinberg_uint32)(l1) & 0x000000FF)      ), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l2) & 0xFF000000) >> 24), (Steinberg_int8)(((Steinberg_uint32)(l2) & 0x00FF0000) >> 16), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l2) & 0x0000FF00) >>  8), (Steinberg_int8)(((Steinberg_uint32)(l2) & 0x000000FF)      ), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l3) & 0xFF000000) >> 24), (Steinberg_int8)(((Steinberg_uint32)(l3) & 0x00FF0000) >> 16), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l3) & 0x0000FF00) >>  8), (Steinberg_int8)(((Steinberg_uint32)(l3) & 0x000000FF)      ), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l4) & 0xFF000000) >> 24), (Steinberg_int8)(((Steinberg_uint32)(l4) & 0x00FF0000) >> 16), \\\n"
    string += "	(Steinberg_int8)(((Steinberg_uint32)(l4) & 0x0000FF00) >>  8), (Steinberg_int8)(((Steinberg_uint32)(l4) & 0x000000FF)      )  \\\n"
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
                        or typedef_return[i] in enum_name:
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
                    or interface_typedef_return[i] in enum_name:
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
        string += "typedef enum\n"
        string += "{\n"
        enum_count = int(len(enum_table[i]) / 2)
        for j in range(enum_count):
            if enum_table[i][2 * j + 1]:
                string += "{} = {}".format(enum_table[i][2 * j], enum_table[i][2 * j + 1])
            else:
                string += "{}".format(enum_table[i][2 * j])
            if j < enum_count - 1:
                string += ","
            string += "\n"
        string += "}} {};\n".format(enum_name[i])
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
        string += "    struct {}Vtbl* lpVtbl;\n".format(interface_name[i])
        string += "{} {};\n".format("}", interface_name[i])
        string += "\n"
        interface_name_clean = interface_name[i][interface_name[i].rindex("_") + 1:]
        if interface_name_clean in ID_table:
            interface_ids = ID_table[interface_name_clean]
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
    string += generate_enums()
    string += generate_variables()
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


# noinspection SpellCheckingInspection
def create_struct_prefix(cursor_type: Type) -> str:
    pointee = cursor_type.get_pointee()
    while pointee.kind != cursor_type.kind.INVALID:
        cursor_type = pointee
        pointee = cursor_type.get_pointee()
    declaration = cursor_type.get_declaration()
    if declaration.kind == declaration.kind.STRUCT_DECL or declaration.kind == declaration.kind.CLASS_DECL:
        return 'struct '
    return ''


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
    for i, token in enumerate(tokens):
        if token.spelling == '::':
            continue
        cursor = token.cursor
        namespace_prefix = ''
        if cursor.kind == cursor.kind.DECL_REF_EXPR or cursor.kind == cursor.kind.TYPE_REF:
            namespace_prefix = create_namespace_prefix(cursor)
        if token.spelling == '(' and previous_kind == cursor.kind.TYPE_REF:
            # e.g.: uint64 (0xffffffff)
            result += ' '
        if token.spelling == ')':
            # insert space after closing bracket, if not followed by another one
            if result and result[-1] == ')':
                result.strip()
            result += f'{token.spelling} '
        elif cursor.kind == cursor.kind.BINARY_OPERATOR:
            # surround binary operators with spaces
            result = result.strip()
            result += f' {token.spelling} '
        else:
            token_with_namespace = namespace_prefix + token.spelling
            if cursor.kind == cursor.kind.TYPE_REF and (i + 1 >= len(tokens) or tokens[i + 1].spelling != ')'):
                token_with_namespace = f'({token_with_namespace})'
            result += token_with_namespace
        previous_kind = cursor.kind
    result = result.strip()
    return result


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


def get_cursor_tokens(cursor: Cursor, use_definition: bool) -> List[Token]:
    result = []
    equal_sign_found = False
    if use_definition:
        cursor_definition = cursor.get_definition()
        if cursor_definition:
            cursor = cursor_definition
        else:
            equal_sign_found = True
    for token in cursor.get_tokens():
        if token.spelling == '=':
            equal_sign_found = True
            continue
        if not equal_sign_found:
            continue
        if not use_definition or token.kind == token.kind.PUNCTUATION or token.kind == token.kind.LITERAL:
            result.append(token)
        else:
            token_cursor = token.cursor
            if token_cursor.kind == token_cursor.kind.TYPE_REF:
                result.append(token)
            else:
                result += get_cursor_tokens(token_cursor, use_definition)
    return result


def replace_expression(cursor: Cursor, use_definition: bool = False) -> str:
    return tokens_to_string(get_cursor_tokens(cursor, use_definition))


def convert_method_args_name(source: str) -> str:
    if source == '_iid':
        return 'iid'
    return source


# ----- conversion function --------------------------------------------------------------------------------------------

def convert_cursor(cursor: Cursor) -> str:
    return create_namespace_prefix(cursor) + cursor.spelling


# noinspection SpellCheckingInspection
def convert_type(cursor_type: Type) -> str:
    num_pointers = 0
    num_consts = 0
    pointee = cursor_type.get_pointee()
    while pointee.kind != pointee.kind.INVALID:
        if cursor_type.is_const_qualified():
            num_consts += 1
        if cursor_type.kind == cursor_type.kind.RVALUEREFERENCE:
            num_pointers += 1
        cursor_type = pointee
        num_pointers += 1
        pointee = cursor_type.get_pointee()
    result = convert_namespace(cursor_type.spelling)
    if num_pointers:
        result = convert_namespace(cursor_type.spelling) + '*' * num_pointers + ' const' * num_consts
    return result


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

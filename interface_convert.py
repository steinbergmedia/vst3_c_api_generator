import re
import sys
from optparse import OptionParser
from pathlib import Path
from typing import List

from clang.cindex import TokenGroup, SourceLocation, Cursor, Type

from clang_helpers import create_translation_unit


# ----- parse ----------------------------------------------------------------------------------------------------------

def parse_header(cursor, include_path):
    for cursor_child in cursor.get_children():
        cursor_child_location = normalise_link(cursor_child.location.file.name)
        if not cursor_child_location.startswith(include_path) or cursor_child_location in includes_table:
            continue
        includes_table.append(cursor_child_location)
        parse_namespace(cursor_child)
        parsing(cursor_child)


def parse_namespace(cursor: Cursor, namespace: str = ''):
    if cursor.kind != cursor.kind.NAMESPACE:
        return
    if namespace:
        namespace += '::'
    namespace += cursor.spelling
    for cursor_child in cursor.get_children():
        parse_namespace(cursor_child, namespace)
        parsing(cursor_child, namespace)


def parsing(cursor: Cursor, namespace: str = ''):
    parse_interfaces(cursor)
    parse_enum(cursor)
    parse_structs(cursor)
    parse_iid(cursor, namespace)
    store_typedefs(cursor)
    parse_variables(cursor)


def parse_iid(cursor: Cursor, namespace: str):
    if cursor.kind != cursor.kind.VAR_DECL or not cursor.spelling.endswith('_iid'):
        return
    id_tokens = _get_token_spellings_from_extent(cursor)
    interface = convert_namespace(namespace)
    if interface:
        interface += '_'
    interface += id_tokens[2]
    id_table[interface] = [id_tokens[4], id_tokens[6], id_tokens[8], id_tokens[10]]


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
        name = '{}[{}]'.format(convert_type(cursor.type), cursor.underlying_typedef_type.element_count)
    else:
        return_type = convert_type(cursor.underlying_typedef_type)
        name = convert_cursor(cursor)
    return return_type, name

# ----- parse interfaces ---------------------------------------------------------------


def parse_interfaces(cursor):
    if cursor.kind != cursor.kind.CLASS_DECL or cursor.spelling in blacklist:
        return
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
        method_count_local = parse_methods(cursor_child, method_count_local)


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

def parse_methods(cursor, method_count_local):
    if cursor.kind == cursor.kind.CXX_METHOD:
        method_count_local = method_count_local + 1
        position = len(interface_name) - 1

        method_args[position].append("")
        method_args[position][method_count_local - 1] = []

        method_name[position].append(cursor.spelling)

        method_return[position].append(create_struct_prefix(cursor.result_type) + convert_type(cursor.result_type))
        method_args_content = parse_method_arguments(cursor)
        method_args[position][method_count_local - 1].append("".join(method_args_content))
    return method_count_local


def parse_method_arguments(cursor):
    p = 0
    method_args_content = []
    for cursor_child in cursor.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        method_args_content.append(create_struct_prefix(cursor_child.type) + convert_type(cursor_child.type))
        method_args_content.append(" ")
        method_args_content.append(_convert_method_args_name(cursor_child.spelling))
        p = p + 1
    return method_args_content


# ----- parse variables ---------------------------------------------------------------


def parse_variables(cursor):
    if cursor.kind == cursor.kind.VAR_DECL and cursor.type.kind == cursor.type.kind.TYPEDEF:
        variable_return.append(convert_type(cursor.type))
        variable_name.append(convert_cursor(cursor))
        variable_value.append(_visit_children(list(cursor.get_children())[-1]))

# ----- parse structs ---------------------------------------------------------------


def parse_structs(cursor):
    if cursor.kind != cursor.kind.STRUCT_DECL or cursor.spelling in blacklist:
        return
    children = list(cursor.get_children())
    if not children:
        return
    struct_table.append(convert_cursor(cursor))
    struct_source.append(convert_cursor_location(cursor.location))
    fields = []
    for cursor_child in children:
        if parse_enum(cursor_child) or cursor_child.kind != cursor_child.kind.FIELD_DECL:
            continue
        cursor_child_type = cursor_child.type
        struct_args = ''
        if cursor_child.type.kind == cursor_child.type.kind.CONSTANTARRAY:
            cursor_child_type = cursor_child_type.element_type
            struct_args = _visit_children(list(cursor_child.get_children())[-1])
        struct_return = create_struct_prefix(cursor_child_type) + convert_type(cursor_child_type)
        field = f'{struct_return} {cursor_child.spelling};'
        if struct_args:
            field = field[:-1] + f'[{struct_args}];'
        fields.append(field)
    struct_content.append(fields)


# ----- parse enums ---------------------------------------------------------------


def parse_enum(cursor: Cursor) -> bool:
    if cursor.kind != cursor.kind.ENUM_DECL:
        return False
    if cursor.spelling:
        enum_name.append(convert_cursor(cursor))
    else:
        enum_name.append('')
    enum_source.append(convert_cursor_location(cursor.location))
    enum_definitions = []
    for cursor_child in cursor.get_children():
        if cursor_child.kind != cursor_child.kind.ENUM_CONSTANT_DECL:
            continue
        enum_definitions.append(create_namespace_prefix(cursor_child) + cursor_child.spelling)
        enum_definitions.append(_visit_children(cursor_child, use_definitions=False))
    enum_table.append(enum_definitions)
    return True


# ----- output to string ---------------------------------------------------------------

# noinspection SpellCheckingInspection
def generate_standard(source_file: str):
    string = "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += 'Source: "{}"\n'.format(_remove_build_path(source_file))
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
        if typedef_return[i]:
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
        if typedef_return[i]:
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


# noinspection SpellCheckingInspection
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
        interface_ids = id_table.get(interface_name[i], None)
        if interface_ids:
            string += "static Steinberg_TUID {}_iid = SMTG_INLINE_UID ({}, {}, {}, {});\n".format(interface_name[i],
                                                                                                  interface_ids[0],
                                                                                                  interface_ids[1],
                                                                                                  interface_ids[2],
                                                                                                  interface_ids[3])
        string += "\n"
    string += "\n"
    return string


# noinspection SpellCheckingInspection
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
        string += ("static {} {} = {};\n".format(variable_return[i], variable_name[i], variable_value[i]))
    string += "\n"
    string += "\n"
    return string


def generate_conversion(source_file: str):
    string = generate_standard(source_file)
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


def _get_binary_operator(cursor: Cursor, children: List[Cursor]) -> str:
    start = children[0].extent.end.offset
    for token in cursor.get_tokens():
        if token.extent.start.offset < start:
            continue
        return token.spelling
    return ''


def _visit_children(cursor: Cursor, use_definitions: bool = True) -> str:
    children = list(cursor.get_children())
    if cursor.kind == cursor.kind.BINARY_OPERATOR:
        operator = _get_binary_operator(cursor, children)
        return '{} {} {}'.format(_visit_children(children[0], use_definitions), operator,
                                 _visit_children(children[1], use_definitions))
    elif cursor.kind == cursor.kind.PAREN_EXPR:
        return '({})'.format(_visit_children(children[0], use_definitions))
    elif cursor.kind == cursor.kind.UNARY_OPERATOR:
        operator = list(cursor.get_tokens())[0].spelling
        return '{}{}'.format(operator, _visit_children(children[0], use_definitions))
    elif cursor.kind == cursor.kind.DECL_REF_EXPR:
        if use_definitions:
            return _visit_children(cursor.get_definition(), use_definitions)
        else:
            return convert_cursor(cursor)
    elif cursor.kind == cursor.kind.UNEXPOSED_EXPR or cursor.kind == cursor.kind.ENUM_CONSTANT_DECL:
        if children:
            return _visit_children(children[0], use_definitions)
        return ''
    elif cursor.kind == cursor.kind.VAR_DECL:
        return _visit_children(children[-1], use_definitions)
    elif cursor.kind == cursor.kind.CSTYLE_CAST_EXPR or cursor.kind == cursor.kind.CXX_FUNCTIONAL_CAST_EXPR:
        return '({}) {}'.format(convert_namespace(children[0].spelling), _visit_children(children[1]), use_definitions)
    elif cursor.kind == cursor.kind.INTEGER_LITERAL or cursor.kind == cursor.kind.STRING_LITERAL:
        if cursor.spelling:
            return cursor.spelling
        return list(cursor.get_tokens())[0].spelling
    else:
        raise TypeError('CursorKind: {} ist not supported!'.format(cursor.kind.name))


def _get_token_spellings_from_extent(cursor: Cursor) -> List[str]:
    cursor_tu = cursor.translation_unit
    extent = cursor_tu.get_extent(cursor.location.file.name, [cursor.extent.start.offset, cursor.extent.end.offset])
    return [token.spelling for token in TokenGroup.get_tokens(cursor_tu, extent)]


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


def _remove_build_path(file_name: str) -> str:
    return re.sub('^.*(pluginterfaces/)', '\\1', normalise_link(file_name))


def convert_cursor_location(cursor_location: SourceLocation) -> str:
    return 'Source: "{}", line {}'.format(_remove_build_path(cursor_location.file.name), cursor_location.line)


def convert_namespace(source: str) -> str:
    return source.replace('::', '_')


def create_namespace_prefix(cursor: Cursor) -> str:
    namespaces = _get_namespaces(cursor)
    if not namespaces:
        return ''
    return '_'.join(namespaces) + '_'


def _get_namespaces(cursor: Cursor) -> List[str]:
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


def _convert_method_args_name(source: str) -> str:
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

id_table = {}


def clear_arrays():
    global interface_source
    global interface_description
    global interface_name
    global inherits_table
    global includes_list
    global includes_table
    global method_name
    global method_return
    global method_args
    global struct_table
    global struct_content
    global struct_source
    global enum_name
    global enum_table
    global enum_source
    global typedef_name
    global typedef_return
    global typedef_interface_name
    global typedef_interface_return
    global interface_typedef_return
    global interface_typedef_name
    global variable_return
    global variable_name
    global variable_value
    global id_table

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

    id_table = {}


# ----- Conversion helper arrays -----
blacklist = ["FUID", "FReleaser"]


if __name__ == '__main__':

    print_header = True
    write_header = True


# ----- Establish Translation Unit -----
    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()
    if not filename:
        print('No filename was specified!')
        exit(1)
    include_path = normalise_link(str(Path(sys.argv[1]).parents[2]))
    tu = create_translation_unit(Path(filename[0]), include_path)

# ----- Parse -----
    parse_header(tu.cursor, include_path)
    header_content = generate_conversion(normalise_link(tu.spelling))

# ----- Write -----
    if write_header:
        header_path = "test_header.h"
        with open(header_path, 'w') as h:
            h.write(header_content)

# ----- Print -----
    if print_header:
        print(header_content)
        print_info()

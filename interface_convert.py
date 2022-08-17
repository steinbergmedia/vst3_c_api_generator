"""
Documentation
------------------------------------------------------------------------------------------------------------------------

This script interprets C++-based COM header files and converts its main structures, that is interfaces,
structs, unions, enums, typedefs and variable declarations into respective C-compatible variants.
The results are assembled into a newly created header file which thus inherits the basic functionality
of its original counterpart.

This conversion is facilitated by the Libclang python bindings library which ports the main functions
of the Clang compiler to python. Using this compiler, the translation unit of the original header file
is established, an abstract syntax tree of nested cursor and token objects which represent the structure
of the original file in an easily accessible way. These objects each contain data about their inherent
characteristics which is selectively parsed and stored for later use when recreating the interfaces.

The script is broken up into several smaller functions which can be sorted into tree main categories,
parsing functions, utility functions and generation functions. Parsing functions interpret the incoming
cursor objects and sort the relevant data into various arrays, aided by the utility functions which
mainly serve to reduce bloat and increase human readability by packaging commonly occurring
structures into short expressions. The generation functions access the previously stored data
to assemble a new C-compatible header file.

The data storage is based on the usage of often multidimensional arrays which each include specific
information about all structures of a certain type in order of their appearance. To facilitate the
unambiguous correlation of these pieces of data, the arrays are always kept in sync and later
accessed using for-loops.

To function properly, the script must be supplied with the original C++ header file, as well as a
working directory that houses all other files this header includes, as these will not be
recognised otherwise.

------------------------------------------------------------------------------------------------------------------------
"""


# ----------------------------------------------------------------------------------------------------------------------
# ----- script begin ---------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
from data_classes import Enum, Container, Interface

"""library import statements"""
import re
import sys
from optparse import OptionParser
from pathlib import Path
from typing import List
from clang.cindex import SourceLocation, Cursor, Type
from clang_helpers import create_translation_unit, TokenGroup, is_not_kind, is_valid, is_kind


# ----------------------------------------------------------------------------------------------------------------------
# ----- parsing functions ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


"""excludes unusable parts and executes parse functions"""
# noinspection SpellCheckingInspection
def parse_header(cursor: Cursor):
    if is_not_kind(cursor, 'TRANSLATION_UNIT'):
        return
    root_path = normalise_link(str(Path(cursor.spelling).parents[2]))
    already_parsed_includes = []
    for cursor_child in cursor.get_children():
        cursor_child_location = normalise_link(cursor_child.location.file.name)
        if not cursor_child_location.startswith(root_path) or cursor_child_location in already_parsed_includes:
            continue
        already_parsed_includes.append(cursor_child_location)
        if parse_namespace(cursor_child):
            continue
        parsing(cursor_child)


"""recursively parses namespaces and executes parse functions"""
# noinspection SpellCheckingInspection
def parse_namespace(cursor: Cursor, namespace: str = '') -> bool:
    if is_not_kind(cursor, 'NAMESPACE'):
        return False
    if namespace:
        namespace += '::'
    namespace += cursor.spelling
    for cursor_child in cursor.get_children():
        if parse_namespace(cursor_child, namespace):
            continue
        parsing(cursor_child, namespace)
    return True


"""executes specific parse functions"""
# noinspection SpellCheckingInspection
def parsing(cursor: Cursor, namespace: str = ''):
    parse_interfaces(cursor)
    parse_enum(cursor)
    parse_structs(cursor)
    parse_iid(cursor, namespace)
    store_typedefs(cursor)
    parse_variables(cursor)


# ----- parse typedefs -------------------------------------------------------------------------------------------------

"""executes typedef parse and stores value"""
# noinspection SpellCheckingInspection
def store_typedefs(cursor):
    return_type, name = parse_typedefs(cursor)
    if return_type and name:
        typedef_return.append(return_type)
        typedef_name.append(name)


"""executes typedef parse and stores value"""
# noinspection SpellCheckingInspection
def store_interface_typedefs(cursor):
    return_type, name = parse_typedefs(cursor)
    if return_type and name:
        interface_typedef_return.append(return_type)
        interface_typedef_name.append(name)


"""parses typedefs and formats output"""
# noinspection SpellCheckingInspection
def parse_typedefs(cursor):
    if is_not_kind(cursor, 'TYPEDEF_DECL') and is_not_kind(cursor, 'TYPE_ALIAS_DECL'):
        return None, None
    if is_kind(cursor.underlying_typedef_type, 'CONSTANTARRAY'):
        return_type = convert_type(cursor.underlying_typedef_type.element_type)
        name = '{}[{}]'.format(convert_type(cursor.type), cursor.underlying_typedef_type.element_count)
    else:
        return_type = convert_type(cursor.underlying_typedef_type)
        name = convert_cursor(cursor)
    return return_type, name


# ----- parse interfaces -----------------------------------------------------------------------------------------------

"""executes all specific interface-related parse functions and stores information"""
# noinspection SpellCheckingInspection
def parse_interfaces(cursor):
    if is_not_kind(cursor, 'CLASS_DECL') or cursor.spelling in blocklist:
        return
    children = list(cursor.get_children())
    if not children:
        # this is only a forward declaration
        return
    interface = Interface(convert_cursor(cursor), get_cursor_location(cursor.location), cursor.brief_comment)
    for cursor_child in children:
        store_interface_typedefs(cursor_child)
        parse_enum(cursor_child)
        parse_inheritance(cursor_child, interface)
        parse_variables(cursor_child)
        parse_methods(cursor_child, interface)
    interfaces.append(interface)


"""parses and stores information about interface inheritance"""
# noinspection SpellCheckingInspection
def parse_inheritance(cursor: Cursor, interface: Interface):
    if is_not_kind(cursor, 'CXX_BASE_SPECIFIER'):
        return
    base_interface_name = convert_namespace(cursor.type.spelling)
    if base_interface_name in interfaces:
        interface.add_base_class(interfaces[base_interface_name])


# ----- parse IIDs -----------------------------------------------------------------------------------------------------

"""parses and stores IIDs of interfaces"""
# noinspection SpellCheckingInspection
def parse_iid(cursor: Cursor, namespace: str):
    if is_not_kind(cursor, 'VAR_DECL') or not cursor.spelling.endswith('_iid'):
        return
    id_tokens = get_id_token_spellings_from_extent(cursor)
    interface_name = convert_namespace(namespace)
    if interface_name:
        interface_name += '_'
    interface_name += id_tokens[2]
    if interface_name in interfaces:
        interfaces[interface_name].set_iid(id_tokens[4], id_tokens[6], id_tokens[8], id_tokens[10])


"""uses tokens to return IID spellings as string"""
# noinspection SpellCheckingInspection
def get_id_token_spellings_from_extent(cursor: Cursor) -> List[str]:
    cursor_tu = cursor.translation_unit
    extent = cursor_tu.get_extent(cursor.location.file.name, [cursor.extent.start.offset, cursor.extent.end.offset])
    return [token.spelling for token in TokenGroup.get_tokens(cursor_tu, extent)]


# ----- parse methods --------------------------------------------------------------------------------------------------

"""executes method argument parse function and stores returned string"""
# noinspection SpellCheckingInspection
def parse_methods(cursor: Cursor, interface: Interface):
    if is_not_kind(cursor, 'CXX_METHOD'):
        return
    method_name = cursor.spelling
    method_return_type = create_struct_prefix(cursor.result_type) + convert_type(cursor.result_type)
    method_args = _parse_method_arguments(cursor)
    interface.add_method (method_name, method_return_type, method_args)


"""parses method arguments and returns formatted string"""
# noinspection SpellCheckingInspection
def _parse_method_arguments(cursor: Cursor) -> List[str]:
    args = []
    for cursor_child in cursor.get_arguments():
        argument_type = create_struct_prefix(cursor_child.type) + convert_type(cursor_child.type)
        name = _convert_method_args_name(cursor_child.spelling)
        args.append(f'{argument_type} {name}')
    return args


"""specific conversion case, not otherwise covered by functions"""
# noinspection SpellCheckingInspection
def _convert_method_args_name(source: str) -> str:
    if source == '_iid':
        return 'iid'
    return source

# ----- specific parse functions ---------------------------------------------------------------------------------------

"""parses and stores variable definition information"""
# noinspection SpellCheckingInspection
def parse_variables(cursor):
    if is_not_kind(cursor, 'VAR_DECL') or is_not_kind(cursor.type, 'TYPEDEF'):
        return
    variable_return.append(convert_type(cursor.type))
    variable_name.append(convert_cursor(cursor))
    variable_value.append(_visit_children(list(cursor.get_children())[-1]))


"""parses, formats and stores struct information, executes union parse function"""
# noinspection SpellCheckingInspection
def parse_structs(cursor):
    if is_not_kind(cursor, 'STRUCT_DECL') or cursor.spelling in blocklist:
        return
    children = list(cursor.get_children())
    if not children:
        # this is only a forward declaration
        return
    fields = []
    for cursor_child in children:
        parse_union(convert_cursor(cursor), cursor_child)
        if parse_enum(cursor_child) or is_not_kind(cursor_child, 'FIELD_DECL'):
            continue
        cursor_child_type = cursor_child.type
        struct_args = ''
        if is_kind(cursor_child.type, 'CONSTANTARRAY'):
            cursor_child_type = cursor_child_type.element_type
            struct_args = _visit_children(list(cursor_child.get_children())[-1])
        struct_return = create_struct_prefix(cursor_child_type) + convert_type(cursor_child_type)
        field = f'{struct_return} {cursor_child.spelling};'
        if struct_args:
            field = field[:-1] + f'[{struct_args}];'
        fields.append(field)
    if fields:
        struct_table.append(convert_cursor(cursor))
        struct_source.append(get_cursor_location(cursor.location))
        struct_content.append(fields)


"""parses and stores union information within a struct"""
# noinspection SpellCheckingInspection
def parse_union(parent, cursor):
    if is_not_kind(cursor, 'UNION_DECL') or cursor.spelling in blocklist:
        return
    children = list(cursor.get_children())
    if not children:
        # this is only a forward declaration
        return
    union_parent.append(parent)
    union_content.append([])
    union_return.append([])
    for cursor_child in children:
        if is_kind(cursor_child, 'FIELD_DECL'):
            union_content[-1].append(convert_cursor(cursor_child))
            union_return[-1].append(convert_type(cursor_child.type))


"""parses and stores enum information"""
# noinspection SpellCheckingInspection
def parse_enum(cursor: Cursor) -> bool:
    if is_not_kind(cursor, 'ENUM_DECL'):
        return False
    if not cursor.spelling:
        return True
    enum = Enum(convert_cursor(cursor), get_cursor_location(cursor.location))
    for cursor_child in cursor.get_children():
        if is_not_kind(cursor_child, 'ENUM_CONSTANT_DECL'):
            continue
        enumerator_name = create_namespace_prefix(cursor_child) + cursor_child.spelling
        enumerator_expression = _visit_children(cursor_child, use_definitions=False)
        enum.add_enumerator(enumerator_name, enumerator_expression)
    enums.append(enum)
    return True


# ----------------------------------------------------------------------------------------------------------------------
# ----- utility functions ----------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

"""returns token spelling after passing extent of first cursor child"""
# noinspection SpellCheckingInspection
def _get_binary_operator(cursor: Cursor, children: List[Cursor]) -> str:
    start = children[0].extent.end.offset
    for token in cursor.get_tokens():
        if token.extent.start.offset < start:
            continue
        return token.spelling
    return ''


"""analyses cursor children, formats and returns string based on CursorKind"""
# noinspection SpellCheckingInspection
def _visit_children(cursor: Cursor, use_definitions: bool = True) -> str:
    children = list(cursor.get_children())
    if is_kind(cursor, 'BINARY_OPERATOR'):
        operator = _get_binary_operator(cursor, children)
        return '{} {} {}'.format(_visit_children(children[0], use_definitions), operator,
                                 _visit_children(children[1], use_definitions))
    elif is_kind(cursor, 'PAREN_EXPR'):
        return '({})'.format(_visit_children(children[0], use_definitions))
    elif is_kind(cursor, 'UNARY_OPERATOR'):
        operator = list(cursor.get_tokens())[0].spelling
        return '{}{}'.format(operator, _visit_children(children[0], use_definitions))
    elif is_kind(cursor, 'DECL_REF_EXPR'):
        if use_definitions:
            return _visit_children(cursor.get_definition(), use_definitions)
        else:
            return convert_cursor(cursor)
    elif is_kind(cursor, 'UNEXPOSED_EXPR') or is_kind(cursor, 'ENUM_CONSTANT_DECL'):
        if children:
            return _visit_children(children[0], use_definitions)
        return ''
    elif is_kind(cursor, 'VAR_DECL'):
        return _visit_children(children[-1], use_definitions)
    elif is_kind(cursor, 'CSTYLE_CAST_EXPR') or is_kind(cursor, 'CXX_FUNCTIONAL_CAST_EXPR')\
            or is_kind(cursor, "CXX_STATIC_CAST_EXPR"):
        return '({}) {}'.format(convert_namespace(children[0].spelling), _visit_children(children[1]), use_definitions)
    elif is_kind(cursor, 'INTEGER_LITERAL') or is_kind(cursor, 'STRING_LITERAL'):
        if cursor.spelling:
            return cursor.spelling
        return list(cursor.get_tokens())[0].spelling
    else:
        raise TypeError('CursorKind: {} ist not supported!'.format(cursor.kind.name))


"""checks if cursor is a struct and returns respective prefix"""
# noinspection SpellCheckingInspection
def create_struct_prefix(cursor_type: Type) -> str:
    pointee = cursor_type.get_pointee()
    while is_valid(pointee):
        cursor_type = pointee
        pointee = cursor_type.get_pointee()
    declaration = cursor_type.get_declaration()
    if is_kind(declaration, 'STRUCT_DECL') or is_kind(declaration, 'CLASS_DECL'):
        return 'struct '
    return ''


"""normalises link nomenclature"""
# noinspection SpellCheckingInspection
def normalise_link(source: str) -> str:
    return source.replace('\\', '/')


"""finds cursor's location and returns it as formatted string"""
# noinspection SpellCheckingInspection
def get_cursor_location(cursor_location: SourceLocation) -> str:
    return 'Source: "{}", line {}'.format(_remove_build_path(cursor_location.file.name), cursor_location.line)


"""removes devise-specific information from generated locations"""
# noinspection SpellCheckingInspection
def _remove_build_path(file_name: str) -> str:
    return re.sub('^.*(pluginterfaces/)', '\\1', normalise_link(file_name))


# ----- namespace functions --------------------------------------------------------------------------------------------

"""formats given namespace prefix and returns it as string"""
# noinspection SpellCheckingInspection
def convert_namespace(source: str) -> str:
    return source.replace('::', '_')


"""gets namespace, formats  prefix and returns it as string"""
# noinspection SpellCheckingInspection
def create_namespace_prefix(cursor: Cursor) -> str:
    namespaces = _get_namespaces(cursor)
    if not namespaces:
        return ''
    return '_'.join(namespaces) + '_'


"""finds cursor's namespace and returns it as string"""
# noinspection SpellCheckingInspection
def _get_namespaces(cursor: Cursor) -> List[str]:
    cursor_definition = cursor.get_definition()
    if cursor_definition:
        cursor = cursor_definition
    cursor = cursor.lexical_parent
    namespaces = []
    while cursor and is_not_kind(cursor, 'TRANSLATION_UNIT'):
        if cursor.spelling:
            namespaces.append(cursor.spelling)
        cursor = cursor.lexical_parent
    namespaces.reverse()
    return namespaces


# ----- conversion functions -------------------------------------------------------------------------------------------


"""attaches namespace prefix to cursor and returns formatted name as string"""
# noinspection SpellCheckingInspection
def convert_cursor(cursor: Cursor) -> str:
    return create_namespace_prefix(cursor) + cursor.spelling


#
# noinspection SpellCheckingInspection
def convert_type(cursor_type: Type) -> str:
    num_pointers = 0
    num_consts = 0
    pointee = cursor_type.get_pointee()
    while is_valid(pointee):
        if cursor_type.is_const_qualified():
            num_consts += 1
        if is_kind(cursor_type, 'RVALUEREFERENCE'):
            num_pointers += 1
        cursor_type = pointee
        num_pointers += 1
        pointee = cursor_type.get_pointee()
    result = convert_namespace(cursor_type.spelling)
    if num_pointers:
        result = convert_namespace(cursor_type.spelling) + '*' * num_pointers + ' const' * num_consts
    return result


# ----------------------------------------------------------------------------------------------------------------------
# ----- generation functions -------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


"""generates standard content for converted header, irrespective of parsed header file, returns string"""
# noinspection SpellCheckingInspection
def generate_standard(source_file: str):
    string = "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += 'Source: "{}"\n'.format(_remove_build_path(source_file))
    string += "\n"
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
    string += "----- Typedefs ---------------------------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    string += generate_typedefs()
    string += "\n"
    string += "\n"
    return string


"""generates formatted typedefs for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_typedefs():
    string = ""
    for typedef in range(len(typedef_name)):
        if typedef_return[typedef]:
            if typedef_return[typedef] in struct_table or typedef_return[typedef] in interfaces\
                    or typedef_return[typedef] in enums:
                string += "typedef struct {} {};\n".format(typedef_return[typedef], typedef_name[typedef])
            else:
                string += "typedef {} {};\n".format(typedef_return[typedef], typedef_name[typedef])
    return string


"""generates formatted typedefs within interfaces for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_interface_typedefs():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Interface typedefs -----------------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for interface_typedef in range(len(interface_typedef_name)):
        if typedef_return[interface_typedef]:
            if interface_typedef_return[interface_typedef] in struct_table\
                or interface_typedef_return[interface_typedef] in interfaces\
                    or interface_typedef_return[interface_typedef] in enums:
                string += "typedef struct {} {};\n".format(interface_typedef_return[interface_typedef],
                                                           interface_typedef_name[interface_typedef])
            else:
                string += "typedef {} {};\n".format(interface_typedef_return[interface_typedef],
                                                    interface_typedef_name[interface_typedef])
    string += "\n"
    string += "\n"
    return string


"""generates formatted forward declarations for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_forward():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Interface forward declarations -----------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for forward_interface in interfaces:
        string += "struct {};\n".format(forward_interface.name)
    string += "\n"
    string += "\n"
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Struct forward declarations --------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for forward_struct in range(len(struct_table)):
        string += "struct {};\n".format(struct_table[forward_struct])
    string += "\n"
    return string


"""generates further standard content for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_result_values():
    string = ""
    string += "\n"
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Result value definitions -----------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    string += "#if COM_COMPATIBLE\n"
    string += "static const Steinberg_tresult Steinberg_kNoInterface = 0x80004002L;\n"
    string += "static const Steinberg_tresult Steinberg_kResultOk = 0x00000000L;\n"
    string += "static const Steinberg_tresult Steinberg_kResultTrue = 0x00000000L;\n"
    string += "static const Steinberg_tresult Steinberg_kResultFalse = 0x00000001L;\n"
    string += "static const Steinberg_tresult Steinberg_kInvalidArgument = 0x80070057L;\n"
    string += "static const Steinberg_tresult Steinberg_kNotImplemented = 0x80004001L;\n"
    string += "static const Steinberg_tresult Steinberg_kInternalError = 0x80004005L;\n"
    string += "static const Steinberg_tresult Steinberg_kNotInitialized = 0x8000FFFFL;\n"
    string += "static const Steinberg_tresult Steinberg_kOutOfMemory = 0x8007000EL;\n"
    string += "\n"
    string += "#else\n"
    string += "static const Steinberg_tresult Steinberg_kNoInterface = -1;\n"
    string += "static const Steinberg_tresult Steinberg_kResultOk = 0;\n"
    string += "static const Steinberg_tresult Steinberg_kResultTrue = 0;\n"
    string += "static const Steinberg_tresult Steinberg_kResultFalse = 1;\n"
    string += "static const Steinberg_tresult Steinberg_kInvalidArgument = 2;\n"
    string += "static const Steinberg_tresult Steinberg_kNotImplemented = 3;\n"
    string += "static const Steinberg_tresult Steinberg_kInternalError = 4;\n"
    string += "static const Steinberg_tresult Steinberg_kNotInitialized = 5;\n"
    string += "static const Steinberg_tresult Steinberg_kOutOfMemory = 6;\n"
    string += "#endif\n"
    string += "\n"
    string += "\n"
    return string


"""generates formatted enums for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_enums():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Enums ------------------------------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for enum in enums:
        string += "/*----------------------------------------------------------------------------------------------------------------------\n"
        string += "{} */\n".format(enum.source_location)
        string += "\n"
        string += "typedef enum\n"
        string += "{\n"
        string += ",\n".join(enum.enumerators)
        string += "\n"
        string += "}} {};\n".format(enum.name)
        string += "\n"
    string += "\n"
    return string


"""generates formatted unions within structs for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_union(parent):
    string = ""
    if parent in union_parent:
        position = union_parent.index(parent)
        string += "    union {\n"
        for union in range(len(union_content[position])):
            if union_return[position][union] in struct_table:
                string += "        struct " + union_return[position][union] + " "
            else:
                string += "        " + union_return[position][union] + " "
            string += union_content[position][union] + ";\n"
        string += "    };\n"
    return string

"""generates formatted structs for converted header, executes union generation function, returns string"""
# noinspection SpellCheckingInspection
def generate_structs():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Structs ----------------------------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for struct in range(len(struct_table)):
        string += "/*----------------------------------------------------------------------------------------------------------------------\n"
        string += "{} */\n".format(struct_source[struct])
        string += "\n"
        string += "struct {} {}\n".format(struct_table[struct], "{")
        for content in range(len(struct_content[struct])):
            string += "    {}\n".format(struct_content[struct][content])
        string += generate_union(struct_table[struct])
        string += "};\n"
        string += "\n"
    string += "\n"
    return string

"""generates formatted interfaces for converted header, executes method generation function, returns string"""
# noinspection SpellCheckingInspection
def generate_interface():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Interfaces -------------------------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for interface in interfaces:
        string += "/*----------------------------------------------------------------------------------------------------------------------\n"
        string += "{} */\n".format(interface.source_location)
        string += "\n"
        string += "typedef struct {}Vtbl\n".format(interface.name)
        string += "{\n"
        for base_class in interface.base_classes:
            string += "    /* methods derived from \"{}\": */\n".format(base_class.name)
            string += "\n".join(base_class.methods)
            string += "\n\n"
        if interface.methods:
            string += "    /* methods defined in \"{}\": */\n".format(interface.name)
            string += "\n".join(interface.methods)
            string += "\n\n"
        string += "{} {}Vtbl;\n".format("}", interface.name)
        string += "\n"
        string += "typedef struct {}\n".format(interface.name)
        string += "{\n"
        string += "    struct {}Vtbl* lpVtbl;\n".format(interface.name)
        string += "{} {};\n".format("}", interface.name)
        string += "\n"
        if interface.iid:
            string += interface.iid
            string += "\n\n"
    string += "\n"
    return string


"""generates formatted variables for converted header, returns string"""
# noinspection SpellCheckingInspection
def generate_variables():
    string = ""
    string += "/*----------------------------------------------------------------------------------------------------------------------\n"
    string += "----- Variable declarations --------------------------------------------------------------------------------------------\n"
    string += "----------------------------------------------------------------------------------------------------------------------*/\n"
    string += "\n"
    for variable in range(len(variable_name)):
        string += ("static {} {} = {};\n".format(variable_return[variable], variable_name[variable], variable_value[variable]))
    string += "\n"
    string += "\n"
    return string


"""executes individual generation functions, returns finalised string"""
# noinspection SpellCheckingInspection
def generate_conversion(source_file: str):
    string = generate_standard(source_file)
    string += generate_forward()
    string += generate_result_values()
    string += generate_interface_typedefs()
    string += generate_enums()
    string += generate_variables()
    string += generate_structs()
    string += generate_interface()
    return string


"""prints information about header file, not necessary for generation process"""
# noinspection SpellCheckingInspection
def print_info():
    print("Number of enums: {}".format(len(enums)))
    for enum in enums:
        print(" {}".format(enum.name))
    print()
    print("Number of structs: {}".format(len(struct_table)))
    for i in range(len(struct_table)):
        print(" {}".format(struct_table[i]))
    print()
    print("Number of interfaces: {}".format(len(interfaces)))
    print()
    for inedex, interface in enumerate(interfaces):
        print("Interface {}: {}".format(inedex + 1, interface.name))
        print(interface.source_location)
        print("Info:", interface.description)
        print("Methods:")
        for method in interface.methods:
            match = re.search('SMTG_STDMETHODCALLTYPE\*\s+([^)]+)', method)
            if match:
                print(" {}".format(match.group(1)))
        print()
    print()


# ----- Arrays ---------------------------------------------------------------------------------------------------------

"""defines all used arrays"""
interfaces = Container()

union_return = []
union_parent = []
union_content = []

struct_table = []
struct_content = []
struct_source = []

enums = Container()

typedef_name = []
typedef_return = []
interface_typedef_return = []
interface_typedef_name = []

variable_return = []
variable_name = []
variable_value = []

blocklist = ["FUID", "FReleaser"]


"""clears all used arrays"""
def clear_arrays():
    global interfaces
    global union_return
    global union_parent
    global union_content
    global struct_table
    global struct_content
    global struct_source
    global enums
    global typedef_name
    global typedef_return
    global interface_typedef_return
    global interface_typedef_name
    global variable_return
    global variable_name
    global variable_value

    interfaces.clear()

    union_return = []
    union_parent = []
    union_content = []

    struct_table = []
    struct_content = []
    struct_source = []

    enums.clear()

    typedef_name = []
    typedef_return = []
    interface_typedef_return = []
    interface_typedef_name = []

    variable_return = []
    variable_name = []
    variable_value = []


# ----------------------------------------------------------------------------------------------------------------------
# ----- main function --------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

    """lets users define the output type"""
    print_header = True
    write_header = True

    """establishes translation unit"""
    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()
    if not filename:
        print('No filename was specified!')
        exit(1)
    include_path = normalise_link(str(Path(sys.argv[1]).parents[2]))
    tu = create_translation_unit(Path(filename[0]), include_path)

    """executes parsing and generation function"""
    parse_header(tu.cursor)
    header_content = generate_conversion(normalise_link(tu.spelling))

    """outputs generated header as new header file"""
    if write_header:
        header_path = "test_header.h"
        with open(header_path, 'w') as h:
            h.write(header_content)

    """outputs generated header in console"""
    if print_header:
        print(header_content)
        print_info()

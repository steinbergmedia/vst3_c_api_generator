import sys
from pathlib import Path
import clang.cindex
from clang.cindex import Config
from optparse import OptionParser

Config.set_library_path("venv/Lib/site-packages/clang/native")

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

def fix_pointers(i, array):
    if i.type.kind == i.type.kind.POINTER:
        array.append(convert(i.type.spelling))
    elif i.type.kind == i.type.kind.LVALUEREFERENCE or i.type.kind == i.type.kind.RVALUEREFERENCE:
        array.append(convert(i.type.spelling))
    else:
        array.append(convert(i.type.spelling))


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

def parse_enum(i):
    if i.kind == i.kind.ENUM_DECL:
        for j in i.get_children():
            if j.kind == j.kind.ENUM_CONSTANT_DECL:
                enum_table.append(j.spelling)
                for k in j.get_children():
                    if k.kind == k.kind.INTEGER_LITERAL or k.kind == k.kind.BINARY_OPERATOR:
                        enum_table.append(array_to_string(get_values_in_extent(k), True))

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

def parse_inheritance(j):
    if j.kind == j.kind.CXX_BASE_SPECIFIER:
        for k in range(len(inherits_table[len(interface_name) - 1]) + 1):
            if normalise_namespace(j.type.spelling) in interface_name:
                inherits_location = interface_name.index(normalise_namespace(j.type.spelling))
                for n in range(len(inherits_table[inherits_location])):
                    inherits_table[len(interface_name) - 1].append(inherits_table[inherits_location][n])
        inherits_table[len(interface_name) - 1].append(normalise_namespace(j.type.spelling))

def convert(source):
    print(source)
    source = normalise_args(source)
    source = remove_spaces(source)
    source = normalise_namespace(source)
    print("  ", source)
    if source in enum_table and not source.isnumeric():
        source = convert(enum_table[enum_table.index(source) + 1])

    elif source in SMTG_table or source in SMTG_table_ptr or source in struct_table_preparse or source in interface_name_preparse:
        source = "SMTG_{}".format(source)
    elif source in SMTG_table_double_ptr or source in struct_table_preparse_double_ptr or source in interface_name_preparse_double_ptr:
        source = "SMTG_{}**".format(source.replace("**", ""))
    elif source in SMTG_table_ptr or source in struct_table_preparse_ptr or source in interface_name_preparse_ptr:
        source = "SMTG_{}*".format(source.replace("*", ""))
    elif source in SMTG_table_rvr or source in struct_table_preparse_rvr or source in interface_name_preparse_rvr:
        source = "SMTG_{}&&".format(source.replace("&&", ""))
    elif source in SMTG_table_lvr or source in struct_table_preparse_lvr or source in interface_name_preparse_lvr:
        source = "SMTG_{}&".format(source.replace("&", ""))

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

    elif source == "_iid":
        source = "iid"
    elif source in remove_table:
        source = ""
    print("     ", source)
    print()
    return source


# ----- print functions ------------------------------------------------------------------------------------------------

def print_structs():
    for i in range(len(struct_table)):
        print("//------------------------------------------------------------------------")
        print(struct_source[i])
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
    for i in range(len(interface_name)):
        print("// ------------------------------------------------------------------------")
        print("// Steinberg::{}".format(interface_name[i]))
        print("// {}".format(interface_source[i]))
        print("// ------------------------------------------------------------------------\n")
        print("typedef struct SMTG_{}Vtbl".format(interface_name[i]))
        print("{")
        print_methods(i)
        print("}", "SMTG_{}Vtbl;\n".format(interface_name[i]))
        print("typedef struct SMTG_{}".format(interface_name[i]))
        print("{")
        print("    SMTG_{}Vtbl* lpVtbl;".format(interface_name[i]))
        print("}", "SMTG_{};\n".format(interface_name[i]))
        #print("SMTG_TUID SMTG_{}_iid = SMTG_INLINE_UID ({}, {}, {}, {});".format(interface_name[i],
        #                                                                         ID_table[i][0],
        #                                                                         ID_table[i][1],
        #                                                                         ID_table[i][2],
        #                                                                         ID_table[i][3]))
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

def print_standard():
    print("#include <stdint.h>\n")
    print("#define SMTG_STDMETHODCALLTYPE\n")
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
    print()

def print_conversion():
    print_standard()
    print_structs()
    print_interface()
    print_info()


# ----- normalise functions --------------------------------------------------------------------------------------------

def normalise_link(string):
    string = str(string)
    return string.replace("\\", "/")

def normalise_namespace(string):
    string = str(string)
    #print(string)
    if "::" in string:
        string = string[string.index("::") + 2:]
        #print(" ", string)
        string = normalise_namespace(string)
    #print()
    return string

def normalise_args(string):
    string = str(string)
    if "[" in string:
        string = string[:string.index("[")]
    return string

def remove_pointers(string):
    string = str(string)
    print(string)
    if " **" in string:
        print(" ", string.replace("**", ""))
        return string.replace("**", "")
    elif " *" in string:
        print(" ", string.replace("*", ""))
        return string.replace("*", ""),
    elif " &&" in string:
        print(" ", string.replace("&&", ""))
        return string.replace("&&", "")
    elif " &" in string:
        print(" ", string.replace("&", ""))
        return string.replace("&", "")

def remove_spaces(string):
    string = str(string)
    if " " in string:
        string = string.replace(" ", "")
    return string







if __name__ == '__main__':

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
    enum_table = []
    struct_table = []
    struct_table_preparse = []
    struct_content = []
    struct_source = []


# ----- Conversion arrays -----
    data_types = ["int32", "char8", "char16", "TUID", "uint32", "ParamID", "String128", "ParamValue", "UnitID"]
    remove_table = ["/*out*/", "/*in*/"]
    SMTG_table = ["char8", "char16", "IBStream", "TChar", "String128", "CString", "MediaType", "BusDirection",
                  "BusType", "IoMode", "UnitID", "ParamValue", "ParamID", "ProgramListID", "CtrlNumber",
                  "TQuarterNotes", "TSamples", "ColorSpec", "kNoParamId", "Sample32", "Sample64", "SampleRate",
                  "SpeakerArrangement", "Speaker", "uchar", "TSize", "tresult", "TBool", "UCoord", "kMaxCoord",
                  "kMinCoord", "AttrID", "ID", "NoteExpressionTypeID", "NoteExpressionValue", "KnobMode"]
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

# ----- Parsing -----
    preparse_header(tu.cursor)
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
    parse_header(tu.cursor)

# ----- Print -----
    print_conversion()
    print(interface_name_preparse)
    print(interface_name_preparse_ptr)


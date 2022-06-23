import sys
from pathlib import Path
import clang.cindex
from clang.cindex import Config
from optparse import OptionParser

Config.set_library_path("venv/Lib/site-packages/clang/native")


def parsing(tu, interface_count, method_count, struct_count):

    l = 0

    for n in tu.get_children():

        if n.kind == n.kind.NAMESPACE:

            namespace_local = n.spelling
            for i in n.get_children():
            # ----- Interfaces ------------------------------------------------------------------

                # ----- Interface name -----
                if i.kind == i.kind.CLASS_DECL:
                    source_interface.append("Source: \"{}\", line {}".format(i.location.file, i.location.line))
                    interface_description.append(i.brief_comment)
                    interface_count = interface_count + 1
                    interface_name.append(i.spelling)

                    inherits_table.append(interface_count)
                    inherits_table[interface_count - 1] = []

                    method_name.append(interface_count)
                    method_name[interface_count - 1] = []

                    method_return.append(interface_count)
                    method_return[interface_count - 1] = []

                    method_args.append(interface_count)
                    method_args[interface_count - 1] = []

                    # ----- Within interface -----

                    method_count_local = 0
                    for j in i.get_children():

                        # ----- Interface inheritance -----

                        inheritance(j, namespace_local)

                        # ----- Methods -----

                        if j.kind == j.kind.CXX_METHOD:
                            method_count = method_count + 1
                            method_count_local = method_count_local + 1

                            method_args[interface_count - 1].append(method_count_local)
                            method_args[interface_count - 1][method_count_local - 1] = []

                            method_name[interface_count - 1].append(j.spelling)
                            method_return[interface_count - 1].append(convert(normalise_namespace(namespace_local, j.result_type.spelling)))

                            method_args_content = get_method_argument_string(j, namespace_local, method_count_local)
                            method_args[interface_count - 1][method_count_local - 1].append("".join(method_args_content))

                # ----- Enums ------------------------------------------------------------------
                parse_enum(i)

                # ----- Structs ------------------------------------------------------------------

                if i.kind == i.kind.STRUCT_DECL:
                    r = 0
                    for j in i.get_children():
                        parse_enum(j)
                        if j.kind == j.kind.FIELD_DECL:
                            struct_args = ""
                            struct_return = ""

                            if r == 0:
                                struct_count = struct_count + 1
                                struct_table.append(i.spelling)
                                struct_content.append(struct_count + 1)
                                struct_content[struct_count - 1] = []
                            for d in j.get_children():
                                if d.kind == d.kind.DECL_REF_EXPR:
                                    struct_args = convert(d.spelling)
                                if d.kind == d.kind.TYPE_REF:
                                    struct_return = convert(normalise_namespace(namespace_local, d.spelling))
                            if struct_args != "":
                                struct_content[struct_count - 1].append("{} {} [{}];".format(struct_return, j.spelling, struct_args))
                            else:
                                struct_content[struct_count - 1].append("{} {};".format(struct_return, j.spelling))
                            r = r + 1

                # ----- ID ------------------------------------------------------------------



                l = l + 1
    return interface_count, method_count, struct_count

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

def print_structs():
    for i in range(struct_count):
        print("//------------------------------------------------------------------------")
        #print("// source: \"{}\"".format(source_file_struct[i]))
        print()
        print("struct SMTG_{} {}".format(struct_table[i], "{"))
        for j in range(len(struct_content[i])):
            print("    {}".format(struct_content[i][j]))
        print("};")
        print()


def inheritance(j, namespace_local):
    if j.kind == j.kind.CXX_BASE_SPECIFIER:
        for k in range(len(inherits_table[interface_count - 1]) + 1):
            if normalise_namespace(namespace_local, j.type.spelling) in interface_name:
                inherits_location = interface_name.index(normalise_namespace(namespace_local, j.type.spelling))
                for n in range(len(inherits_table[inherits_location])):
                    inherits_table[interface_count - 1].append(inherits_table[inherits_location][n])
        inherits_table[interface_count - 1].append(normalise_namespace(namespace_local, j.type.spelling))

def get_method_argument_string(j, namespace_local, method_count_local):
    p = 0
    method_args_content = []
    for k in j.get_arguments():
        if p > 0:
            method_args_content.append(", ")
        if k.type.kind == k.type.kind.POINTER:
            method_args_content.append(convert(normalise_namespace(namespace_local, k.type.spelling).replace(" *", "")))
            method_args_content.append("*")
        else:
            method_args_content.append(convert(normalise_namespace(namespace_local, k.type.spelling)))
        method_args_content.append(" ")
        method_args_content.append(convert(k.spelling))
        p = p + 1
    return method_args_content

def get_methods(j, method_count, method_count_local, namespace_local):
    if j.kind == j.kind.CXX_METHOD:
        method_count = method_count + 1
        method_count_local = method_count_local + 1

        method_args[interface_count - 1].append(method_count_local)
        method_args[interface_count - 1][method_count_local - 1] = []

        method_name[interface_count - 1].append(j.spelling)
        method_return[interface_count - 1].append(convert(normalise_namespace(namespace_local, j.result_type.spelling)))

        method_args_content = get_method_argument_string(j, namespace_local, method_count_local)
        method_args[interface_count - 1][method_count_local - 1].append(array_to_string(method_args_content, False))

        return method_count

def convert(source):
    if source in enum_table and not source.isnumeric():
        source = convert(enum_table[enum_table.index(source) + 1])
    elif source in SMTG_table or source in SMTG_table_ptr or source in struct_table or source in interface_name:
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
    for i in range(interface_count):
        print("// ------------------------------------------------------------------------")
        print("// Steinberg::{}".format(interface_name[i]))
        print("// {}".format(source_interface[i]))
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
    for i in range(interface_count):
        print("Interface {}: {}".format(i + 1, interface_name[i]))
        print(source_interface[i])
        print(interface_description[i])
        print("Inherits:")
        for j in range(len(inherits_table[i])):
            print(inherits_table[i][j])
        print("Methods:")
        for j in range(method_count):
            if j < len(method_name[i]):
                print(method_name[i][j])
        print()


def normalise_link(path):
    path = str(path)
    return path.replace("\\", "/")

def normalise_namespace(namespace_local, path):
    path = str(path)
    return path.replace("{}::".format(namespace_local), "")

if __name__ == '__main__':

# ----- Establish Translation Unit -----
    parser = OptionParser("usage: {filename} [clang-args*]")
    (opts, filename) = parser.parse_args()
    index = clang.cindex.Index.create()
    include_path = normalise_link(Path(sys.argv[1]).parents[2])
    tu = index.parse(normalise_link(filename[0]), ['-I', include_path, '-x', 'c++-header'])
    source_file = normalise_link(tu.spelling)

# ----- Arrays -----
    source_interface = []
    interface_description = []
    interface_name = []
    inherits_table = []
    tu_table_temp = []
    tu_table_spelling = []
    tu_table = []
    includes_list = []
    method_name = []
    method_return = []
    method_args = []
    enum_table = []
    struct_table = []
    struct_content = []


# ----- Variables -----
    interface_count = 0
    method_count = 0
    struct_count = 0


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
    _t_table_ptr = []
    SMTG_TUID_table_ptr = []



# ----- Parsing -----
    interface_count, method_count, struct_count = parsing(tu.cursor, interface_count, method_count, struct_count)

# ----- Print -----
    print_structs()
    print_interface()
    print_info()
    #print(struct_table)
    #print(enum_table)

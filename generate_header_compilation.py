

from os import listdir
from os.path import isfile, join

print_header_file = True
create_header_file = True

header_list = [f for f in listdir("_deps/pluginterfaces/vst") if isfile(join("C:/Projekt3/toolchain_c_interface/build/_deps/pluginterfaces/vst", f))]
print(header_list)

if print_header_file:
    print("//------------------------------------------------------------------------")
    print("// Project     : VST SDK")
    print("//")
    print("// Category    : Interfaces")
    print("// Filename    : pluginterfaces/vst/header_compilation.h")
    print("// Created by  : Steinberg, 06/2022")
    print("// Description : VST Edit Controller Interfaces")
    print("//")
    print("//-----------------------------------------------------------------------------")
    print("// This file is part of a Steinberg SDK. It is subject to the license terms")
    print("// in the LICENSE file found in the top-level directory of this distribution")
    print("// and at www.steinberg.net/sdklicenses.")
    print("// No part of the SDK, including this file, may be copied, modified, propagated,")
    print("// or distributed except according to the terms contained in the LICENSE file.")
    print("//-----------------------------------------------------------------------------")
    print()
    print("#pragma once")
    print()
    for i in range(len(header_list)):
        print("#include \"pluginterfaces/vst/{}\"".format(header_list[i]))
    print()

if create_header_file:
    header_path = "_deps/pluginterfaces/vst/header_compilation.h"
    with open(header_path, 'w') as h:
        h.write("//------------------------------------------------------------------------\n")
        h.write("// Project     : VST SDK\n")
        h.write("//\n")
        h.write("// Category    : Interfaces\n")
        h.write("// Filename    : pluginterfaces/vst/header_compilation.h\n")
        h.write("// Created by  : Steinberg, 06/2022\n")
        h.write("// Description : VST Edit Controller Interfaces\n")
        h.write("//\n")
        h.write("//-----------------------------------------------------------------------------\n")
        h.write("// This file is part of a Steinberg SDK. It is subject to the license terms\n")
        h.write("// in the LICENSE file found in the top-level directory of this distribution\n")
        h.write("// and at www.steinberg.net/sdklicenses.\n")
        h.write("// No part of the SDK, including this file, may be copied, modified, propagated,\n")
        h.write("// or distributed except according to the terms contained in the LICENSE file.\n")
        h.write("//-----------------------------------------------------------------------------\n")
        h.write("\n")
        h.write("#pragma once\n")
        h.write("\n")
        for i in range(len(header_list)):
            h.write("#include \"pluginterfaces/vst/{}\"\n".format(header_list[i]))
from os import listdir
from os.path import isfile, join

print_header_file = True
create_header_file = True

header_list = [f for f in listdir("_deps/pluginterfaces/vst") if isfile(join("_deps/pluginterfaces/vst", f))]

def generate_header():
    string ="//------------------------------------------------------------------------\n"
    string += "// Project     : VST SDK\n"
    string += "//\n"
    string += "// Category    : Interfaces\n"
    string += "// Filename    : pluginterfaces/vst/header_compilation.h\n"
    string += "// Created by  : Steinberg, 06/2022\n"
    string += "// Description : VST Edit Controller Interfaces\n"
    string += "//\n"
    string += "//-----------------------------------------------------------------------------\n"
    string += "// This file is part of a Steinberg SDK. It is subject to the license terms\n"
    string += "// in the LICENSE file found in the top-level directory of this distribution\n"
    string += "// and at www.steinberg.net/sdklicenses.\n"
    string += "// No part of the SDK, including this file, may be copied, modified, propagated,\n"
    string += "// or distributed except according to the terms contained in the LICENSE file.\n"
    string += "//-----------------------------------------------------------------------------\n"
    string += "\n"
    string += "#pragma once\n"
    string += "\n"
    string += "#include \"pluginterfaces/gui/iplugview.h\"\n"
    string += "#include \"pluginterfaces/gui/iplugviewcontentscalesupport.h\"\n"
    string += "#include \"pluginterfaces/base/ibstream.h\"\n"
    for i in range(len(header_list)):
        string += "#include \"pluginterfaces/vst/{}\"\n".format(header_list[i])
    return string

header_string = generate_header()

# ----- Write -----
if create_header_file:
    header_path = "_deps/pluginterfaces/vst/header_compilation.h"
    with open(header_path, 'w') as h:
        h.write(header_string)

if print_header_file:
    print(header_string)

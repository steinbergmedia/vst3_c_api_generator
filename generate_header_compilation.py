from pathlib import Path

print_header_file = True
create_header_file = True


# noinspection SpellCheckingInspection
def _generate_header(pluginterfaces_path):
    string = "//------------------------------------------------------------------------\n"
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
    for file in ['gui/iplugviewcontentscalesupport.h', 'base/ibstream.h']:
        string += f'#include "pluginterfaces/{file}"\n'
    for file in (pluginterfaces_path / 'vst').iterdir():
        string += f'#include "pluginterfaces/vst/{file.name}"\n'
    return string


# noinspection SpellCheckingInspection
def main():
    pluginterfaces_path = Path(__file__).parent / 'build' / '_deps' / 'pluginterfaces'
    header_string = _generate_header(pluginterfaces_path)

    if create_header_file:
        with (pluginterfaces_path / 'vst' / 'header_compilation.h').open('w') as h:
            h.write(header_string)

    if print_header_file:
        print(header_string)


if __name__ == '__main__':
    main()

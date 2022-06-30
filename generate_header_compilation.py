from pathlib import Path

from file_string import FileString

print_header_file = True
create_header_file = True


# noinspection SpellCheckingInspection
def _generate_header(pluginterfaces_path):
    result = FileString()
    result /= '//------------------------------------------------------------------------'
    result /= '// Project     : VST SDK'
    result /= '//'
    result /= '// Category    : Interfaces'
    result /= '// Filename    : pluginterfaces/vst/header_compilation.h'
    result /= '// Created by  : Steinberg, 06/2022'
    result /= '// Description : VST Edit Controller Interfaces'
    result /= '//'
    result /= '//-----------------------------------------------------------------------------'
    result /= '// This file is part of a Steinberg SDK. It is subject to the license terms'
    result /= '// in the LICENSE file found in the top-level directory of this distribution'
    result /= '// and at www.steinberg.net/sdklicenses.'
    result /= '// No part of the SDK, including this file, may be copied, modified, propagated,'
    result /= '// or distributed except according to the terms contained in the LICENSE file.'
    result /= '//-----------------------------------------------------------------------------'
    result /= ''
    result /= '#pragma once'
    result /= ''
    for file in ['gui/iplugviewcontentscalesupport.h', 'base/ibstream.h']:
        result /= f'#include "pluginterfaces/{file}"'
    for file in (pluginterfaces_path / 'vst').iterdir():
        result /= f'#include "pluginterfaces/vst/{file.name}"'
    return result


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

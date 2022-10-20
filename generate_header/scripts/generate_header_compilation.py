#-----------------------------------------------------------------------------
# This file is part of a Steinberg SDK. It is subject to the license terms
# in the LICENSE file found in the top-level directory of this distribution
# and at www.steinberg.net/sdklicenses. 
# No part of the SDK, including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.
#-----------------------------------------------------------------------------

import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


# noinspection SpellCheckingInspection
def _generate_header(pluginterfaces_path, result_path):
    blocklist = ['ivsttestplugprovider.h']
    pluginterfaces_includes = []
    for file in ['gui/iplugviewcontentscalesupport.h', 'gui/iplugview.h', 'base/ibstream.h']:
        pluginterfaces_includes.append(file)
    for file in (pluginterfaces_path / 'vst').iterdir():
        if file.name in blocklist:
            continue
        pluginterfaces_includes.append('vst/{}'.format(file.name))
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / 'templates'), trim_blocks=True)
    template = env.get_template(result_path.name)
    file_name = result_path.relative_to(result_path.parents[2])
    today = date.today().strftime("%m/%Y")
    content = template.render(file_name=file_name, date=today, pluginterfaces_includes=pluginterfaces_includes)
    with result_path.open('w') as result_file:
        result_file.write(content)
    return content


# noinspection SpellCheckingInspection
def main():
    if len(sys.argv) < 2:
        print('Pluginterfaces source directory was not specified!')
        exit(1)
    pluginterfaces_path = Path(sys.argv[1])
    result_path = pluginterfaces_path / 'vst' / 'header_compilation.h'
    print(_generate_header(pluginterfaces_path, result_path))


if __name__ == '__main__':
    main()

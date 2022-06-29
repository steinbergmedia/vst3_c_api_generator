from pathlib import Path

import clang


def set_library_path():
    libclang_path = Path(clang.__file__).parent / 'native'
    clang.cindex.Config.set_library_path(str(libclang_path))

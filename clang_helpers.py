from pathlib import Path

import clang


def set_library_path():
    libclang_path = Path(clang.__file__).parent / 'native'
    clang.cindex.Config.set_library_path(str(libclang_path))


def create_translation_unit(header_path: Path, include_path: str):
    set_library_path()
    return clang.cindex.Index.create().parse(header_path, ['-I', include_path, '-x', 'c++-header'])

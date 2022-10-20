#-----------------------------------------------------------------------------
# This file is part of a Steinberg SDK. It is subject to the license terms
# in the LICENSE file found in the top-level directory of this distribution
# and at www.steinberg.net/sdklicenses. 
# No part of the SDK, including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.
#-----------------------------------------------------------------------------

from pathlib import Path

import clang
from clang.cindex import CursorKind, TypeKind, Cursor, Type
# noinspection PyProtectedMember
from clang.cindex import TokenGroup as TGroup


def set_library_path():
    if clang.cindex.Config.library_path:
        return
    libclang_path = Path(clang.__file__).parent / 'native'
    clang.cindex.Config.set_library_path(str(libclang_path))


def create_translation_unit(header_path: Path, include_path: str):
    set_library_path()
    return clang.cindex.Index.create().parse(header_path, ['-I', include_path, '-x', 'c++-header'])


def is_kind(cursor_or_type: [Cursor, Type], kind: str) -> bool:
    if type(cursor_or_type) == Cursor:
        kind_class = CursorKind
    else:
        kind_class = TypeKind
    return cursor_or_type.kind == kind_class.__dict__.get(kind, None)


def is_not_kind(cursor_or_type: [Cursor, Type], kind: str) -> bool:
    return not is_kind(cursor_or_type, kind)


def is_valid(cursor_type: Type) -> bool:
    return is_not_kind(cursor_type, 'INVALID')


TokenGroup = TGroup

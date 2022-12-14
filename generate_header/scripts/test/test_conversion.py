#-----------------------------------------------------------------------------
# This file is part of a Steinberg SDK. It is subject to the license terms
# in the LICENSE file found in the top-level directory of this distribution
# and at www.steinberg.net/sdklicenses. 
# No part of the SDK, including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.
#-----------------------------------------------------------------------------

import re
import unittest
from pathlib import Path

from interface_convert import create_translation_unit, parse_header, generate_conversion, normalise_link, clear_arrays


class TestConversion(unittest.TestCase):
    def setUp(self):
        clear_arrays()

    @classmethod
    def _convert_header(cls, header_name: str) -> str:
        header_path = (cls._get_headers_directory() / f'{header_name}.h').absolute()
        translation_unit = create_translation_unit(header_path, str(header_path.parents[2]))
        parse_header(translation_unit.cursor)
        result = generate_conversion(normalise_link(translation_unit.spelling))
        translation_unit.reparse(unsaved_files=[(header_path, '')])
        return result

    @classmethod
    def _load_expectation(cls, header_name: str) -> str:
        expectation_path = cls._get_headers_directory() / f'{header_name}_expected.h'
        with expectation_path.open() as f:
            return f.read()

    @staticmethod
    def _get_section(start_comment: str, end_comment: str, header_content: str) -> str:
        if end_comment:
            match = re.search(r'{}.*?\*/\s*(.*?)\s*/\*-+\s-+.-+.{}'.format(start_comment, end_comment), header_content,
                              flags=re.DOTALL)
        else:
            match = re.search(r'{}.*?\*/\s*(.*?)$'.format(start_comment), header_content, flags=re.DOTALL)
        if match:
            return re.sub(r'.?/\*-----.*?\*/.', '', match.group(1), flags=re.DOTALL).strip()
        return ''

    @staticmethod
    def _get_headers_directory():
        return Path(__file__).parent / 'headers'

    def test_variables(self):
        header_name = 'variables'
        content_section = self._get_section('Variable declarations', 'Structs', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

    def test_enums(self):
        header_name = 'enums'
        content_section = self._get_section('Enums', 'Variable declarations', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

    def test_struct(self):
        header_name = 'structs'
        content_section = self._get_section('Structs', 'Interfaces', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

    def test_interfaces(self):
        header_name = 'interfaces'
        content_section = self._get_section('Interfaces', '', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

    def test_typedefs(self):
        header_name = 'typedefs'
        generated_source = self._convert_header(header_name)
        content_section = self._get_section('Typedefs', 'Interface forward declarations', generated_source)
        content_section += '\n\n'
        content_section += self._get_section('Interface typedefs', 'Enums', generated_source)
        self.assertEqual(self._load_expectation(header_name), content_section)

    def test_vst_interfaces(self):
        header_name = 'vst_interfaces'
        content_section = self._get_section('Interfaces', '', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

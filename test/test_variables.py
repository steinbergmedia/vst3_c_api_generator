import re
import unittest
from pathlib import Path

from interface_convert import create_translation_unit, parse_header, generate_conversion, normalise_link


class TestConversion(unittest.TestCase):
    def tearDown(self):
        path = Path(__file__).parent / 'test_header.h'
        path.unlink()

    @staticmethod
    def _convert_header(header_name: str) -> str:
        header_path = Path('headers', f'{header_name}.h').absolute()
        include_path = str(header_path.parents[2])
        translation_unit = create_translation_unit(header_path, include_path)
        parse_header(translation_unit.cursor, include_path)
        return generate_conversion(normalise_link(translation_unit.spelling))

    @staticmethod
    def _load_expectation(header_name: str) -> str:
        expectation_path = Path('headers', f'{header_name}_expected.h')
        with expectation_path.open() as f:
            return f.read()

    @staticmethod
    def _get_section(comment_string: str, header_content: str) -> str:
        match = re.search(r'{}.*?\*/\s*(.*?)\s*(/\*|$)'.format(comment_string), header_content, re.DOTALL)
        if match:
            return match.group(1)
        return ''

    def test_variables(self):
        header_name = 'variables'
        content_section = self._get_section('Variable declarations', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

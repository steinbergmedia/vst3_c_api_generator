import re
import unittest
from pathlib import Path

from interface_convert import create_translation_unit, parse_header, generate_conversion, normalise_link, clear_arrays


class TestConversion(unittest.TestCase):
    def setUp(self):
        clear_arrays()

    @staticmethod
    def _convert_header(header_name: str) -> str:
        header_path = Path('headers', f'{header_name}.h').absolute()
        include_path = str(header_path.parents[2])
        translation_unit = create_translation_unit(header_path, include_path)
        parse_header(translation_unit.cursor, include_path)
        result = generate_conversion(normalise_link(translation_unit.spelling))
        translation_unit.reparse(unsaved_files=[(header_path, '')])
        return result

    @staticmethod
    def _load_expectation(header_name: str) -> str:
        expectation_path = Path('headers', f'{header_name}_expected.h')
        with expectation_path.open() as f:
            return f.read()

    @staticmethod
    def _get_section(start_comment: str, end_comment: str, header_content: str) -> str:
        match = re.search(r'{}.*?\*/\s*(.*?)\s*/\*-+.{}'.format(start_comment, end_comment), header_content,
                          flags=re.DOTALL)
        if match:
            return re.sub(r'.?/\*.*?\*/.', '', match.group(1), flags=re.DOTALL).strip()
        return ''

    def test_variables(self):
        header_name = 'variables'
        content_section = self._get_section('Variable declarations', 'Structs', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)

    def test_enums(self):
        header_name = 'enums'
        content_section = self._get_section('Enums', 'Variable declarations', self._convert_header(header_name))
        self.assertEqual(self._load_expectation(header_name), content_section)
from typing import List


class Container(list):
    def __contains__(self, name: str) -> bool:
        for element in self:
            if element.name == name:
                return True
        return False

    def __getitem__(self, name: str):
        for element in self:
            if element.name == name:
                return element
        return None


class Enum:
    def __init__(self, name: str, source_location: str):
        self._name = name
        self._source_location = source_location
        self._enumerators = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_location(self) -> str:
        return self._source_location

    @property
    def enumerators(self) -> List[str]:
        return self._enumerators

    def add_enumerator(self, name, expression):
        enumerator = name
        if expression:
            enumerator += f' = {expression}'
        self._enumerators.append(enumerator)


class Interface:
    def __init__(self, name: str, source_location: str, description: str):
        self._name = name
        self._source_location = source_location
        self._description = description
        self._base_classes = []
        self._methods = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_location(self) -> str:
        return self._source_location

    @property
    def description(self) -> str:
        return self._description

    @property
    def methods(self) -> List[str]:
        return self._methods

    @property
    def base_classes(self) -> List["Interface"]:
        result = []
        for base_class in self._base_classes:
            for base_base_class in base_class.base_classes:
                if base_base_class not in result:
                    result.append(base_base_class)
            if base_class not in result:
                result.append(base_class)
        return result

    # noinspection SpellCheckingInspection
    def add_method(self, name, return_type, args):
        method = f'    {return_type} (SMTG_STDMETHODCALLTYPE* {name}) (void* thisInterface'
        if args:
            method += ', ' + ', '.join(args)
        method += ');'
        self._methods.append(method)

    def add_base_class(self, base_interface):
        self._base_classes.append(base_interface)

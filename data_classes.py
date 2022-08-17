from typing import List


class Container(list):
    def __contains__(self, name):
        for element in self:
            if element.name == name:
                return True
        return False


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

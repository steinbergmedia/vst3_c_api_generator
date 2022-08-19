class FileString(str):
    def __new__(cls, content=''):
        return super().__new__(cls, content)

    def __truediv__(self, key):
        return FileString(self + key + '\n')

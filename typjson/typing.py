NoneType = type(None)


class char(str):
    def __new__(cls, content):
        if len(content) != 1:
            raise ValueError
        return str.__new__(cls, content)

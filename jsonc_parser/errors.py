class FunctionParameterError(Exception):
    """
    This excption indicates that one or more of function's parameters are incorrect
    """

    def __init__(self, *args):
        self.__msg = args[0]
        super().__init__(self.__msg)

    def __str__(self):
        return self.__msg


class FileError(Exception):
    """
    This exception indicates that file format cannot be parsed
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return super().__str__()


class ParserError(Exception):
    """
    This exception indicates that file cannot be parsed
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return super().__str__()
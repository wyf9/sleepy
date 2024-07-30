import json
import re
from jsonc_parser.errors import FileError, FunctionParameterError, ParserError
import os
from typing import Union


class JsoncParser:

    # regex = re.compile(r"//.*?\n|/\*.*?\*/", re.MULTILINE | re.DOTALL)
    regex = re.compile(r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)", re.MULTILINE | re.DOTALL)
    newline_replace_regex = re.compile("\n{2,}", re.MULTILINE)

    def parse_str(_string: str) -> dict:
        """
        Parse JSON-as-string and deserialize its content into Python dictionary,
        ignoring any comments.

        Parameters: `_string:str` - path to file

        This function will raise a `FunctionParameterError` exception if `_string` parameter
        has an incorrect type or is empty.
        This function will raise a `ParserError` exception if the string cannot be parsed.
        This function will raise any additional exceptions if occurred.
        """

        def __re_sub(match):
            if match.group(2) is not None:
                return ""
            else:
                return match.group(1)

        if type(_string) != str:
            raise FunctionParameterError(
                "_string parameter must be str; got {} instead".format(type(_string).__name__)
            )

        try:
            data = JsoncParser.regex.sub(__re_sub, _string)
            return json.loads(JsoncParser.regex.sub(__re_sub, data))
        except Exception as e:
            raise ParserError("{} file cannot be parsed (message: {})".format(_string, str(e)))

    @staticmethod
    def parse_file(filepath: Union[str, os.PathLike], encoding: str = None) -> dict:
        """
        Parse .jsonc file and deserialize its content into Python dictionary,
        ignoring any comments.

        Parameters:
            `filepath: str | os.PathLike` - path to file
            `encoding: str = None` - option of open()

        This function will raise a `FunctionParameterError` exception if `filepath` parameter
        has an incorrect type or is empty.
        This function will raise a `FileError` exception if file format is unsupported.
        This function will raise a `ParserError` exception if file cannot be parsed.
        This function will raise any additional exceptions if occurred.
        """

        def __re_sub(match):
            if match.group(2) is not None:
                return ""
            else:
                return match.group(1)
        
        # verify that provided path is a valid path-like object
        try:
            filepath = os.fspath(filepath)
        except TypeError:
            raise FunctionParameterError(
                "filepath parameter must be path-like; got {} instead".format(type(filepath).__name__)
            )

        if not filepath:
            raise FunctionParameterError("path is empty.")

        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise FileError("{} does not exist or is not a file".format(filepath))

        if filepath.split(".")[-1] not in ["json", "jsonc"]:
            raise FileError("file {} has an unsupported extension.".format(filepath))

        json_file = open(filepath, "r", encoding=encoding)
        data_raw = json_file.read()
        json_file.close()

        try:
            data = JsoncParser.regex.sub(__re_sub, data_raw)
            return json.loads(JsoncParser.regex.sub(__re_sub, data))
        except Exception as e:
            raise ParserError("{} file cannot be parsed (message: {})".format(filepath, str(e)))

    @staticmethod
    def convert_to_json(
        filepath: Union[str, os.PathLike],
        remove_file: bool = False,
        encoding: str = None,
        ensure_ascii: bool = True,
    ) -> None:
        """
        Convert file from .jsonc to .json format, removing any comments from it

        Parameters: `path: str | os.PathLike` is a path to file, `remove_file:bool` indicates if
        source file will be deleted or not. If set to True, .jsonc file will be deleted from the
        hard drive, otherwise file remains alongside with its .json output.
            `encoding: str = None` - option of open()
            `ensure_ascii: bool = True` - option of json.dump()

        This function will raise a `FunctionParameterError` if one or more of function's parameters
        has an incorrect type/invalid value.
        This function will raise any additional exceptions if occurred.

        """

        # verify that provided path is a valid path-like object
        try:
            filepath = os.fspath(filepath)
        except TypeError:
            raise FunctionParameterError(
                "filepath parameter must be path-like; got {} instead".format(type(filepath).__name__)
            )

        if not filepath:
            raise FunctionParameterError("path is empty.")

        if type(remove_file) != bool:
            raise FunctionParameterError(
                "remove_file parameter must be bool; got {} instead.".format(
                    type(remove_file).__name__
                )
            )

        data = JsoncParser.parse_file(filepath, encoding=encoding)

        if remove_file:
            os.remove(filepath)

        new_filename = os.path.splitext(filepath)[0] + ".json"
        if os.path.exists(new_filename) and os.path.isfile(new_filename):
            raise FileError("{} file already exists".format(new_filename))

        json_file = open(new_filename, "x", encoding=encoding)
        json_file.write(json.dumps(data, indent=2, ensure_ascii=ensure_ascii))
        json_file.close()

    @staticmethod
    def convert_to_jsonc(
        filepath: Union[str, os.PathLike],
        remove_file: bool = False,
        encoding: str = None,
        ensure_ascii: bool = True
    ):
        """
        Convert file .jsonc format, enabling comments.

        Parameters: `filepath: str | os.PathLike` is a path to file, `remove_file:bool` indicates
        if source file will be deleted or not. If set to True, .json file will be deleted from the
        hard drive, otherwise file remains alongside with its .jsonc output.
            `encoding: str = None` - option of open()
            `ensure_ascii: bool = True` - option of json.dump()

        This function will raise a `FunctionParameterError` if one or more of function's parameters
        has an incorrect type/invalid value.
        This function will raise any additional exceptions if occurred.
        """
        # verify that provided path is a valid path-like object
        try:
            filepath = os.fspath(filepath)
        except TypeError:
            raise FunctionParameterError(
                "filepath parameter must be path-like; got {} instead".format(type(filepath).__name__)
            )

        if not filepath:
            raise FunctionParameterError("path is empty.")

        if type(remove_file) != bool:
            raise FunctionParameterError(
                "remove_file parameter must be bool; got {} instead.".format(
                    type(remove_file).__name__
                )
            )

        data = JsoncParser.parse_file(filepath, encoding=encoding)

        if remove_file:
            os.remove(filepath)

        new_filename = os.path.splitext(filepath)[0] + ".jsonc"
        if os.path.exists(new_filename) and os.path.isfile(new_filename):
            raise FileError("{} file already exists".format(new_filename))

        json_file = open(new_filename, "x", encoding=encoding)
        json_file.write(json.dumps(data, indent=2, ensure_ascii=ensure_ascii))
        json_file.close()

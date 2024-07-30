本文件夹中的内容来自 [kobayashi-deepinsight/jsonc-parser](https://github.com/kobayashi-deepinsight/jsonc-parser)

> 以下为原文件内容

# jsonc-parser

This package is a lightweight, zero-dependency module for parsing files with .jsonc extension. (<i>a.k.a. JSON with comments</i>)

## Installation

To install this package, simply download it from [PyPI](https://pypi.org/project/jsonc-parser):

    pip install jsonc-parser

Also you can build it yourself from source code available on [GitHub](https://github.com/NickolaiBeloguzov/jsonc-parser)

## Usage

You need to just import _JsoncParser_ class from this package:

    from jsonc_parser.parser import JsoncParser

This class requires no instance to function (i.e. it is fully static)

## Functions

These are all methods that JsoncParser class provides for working with .jsonc files:

-   ##### JsoncParser.parse_file(filepath: PathLike) -> dict

    This function parses file, specified in _filepath_ parameter, and deserializes it into a valid Python object (dictionary), removing any comment in the process. No alterations are made it the file itself. _filepath_ parameter specifies path to .jsonc file.

        from jsonc_parser.parser import JsoncParser

        file_path = "./data.jsonc"
        # Content from 'data.jsonc' -> {"version": "1.0.0" /*This is my project's version*/}

        data = JsoncParser.parse_file(file_path)

        print(data)
        # Output: {'version': '1.0.0'}

    This function can raise _[FunctionParameterError](#exc-function-parameter-error)_ if filepath parameter is not a path-like object (str, bytes object representing a path, or os.PathLike compliant) or is empty. Also this function will raise _[FileError](#exc-file-error)_ exception if file's format is unsupported and a _[ParserError](#exc-parser-error)_ exception if file cannot be parsed/contains invalid JSON data.

-   ##### JsoncParser.parse_str(_string: str) -> dict

    This function parses string, specified in __string_ parameter, and deserializes it into a valid Python object (dictionary), removing any comment in the process.

        from jsonc_parser.parser import JsoncParser

        json_string = """{"version": "1.0.0" /*This is my project's version*/}"""

        data = JsoncParser.parse_str(json_string)

        print(data)
        # Output: {'version': '1.0.0'}

    This function can raise _[FunctionParameterError](#exc-function-parameter-error)_ if __string_ parameter is not a string or is empty. Also this function will raise a _[ParserError](#exc-parser-error)_ exception if file cannot be parsed/contains invalid JSON data.

    ##### JsoncParser.convert_to_json(filepath: PathLike, remove_file: bool = False) -> None
    This function converts file from .jsonc to .json format, removing any comments in the process. filepath parameter specifies path to file and remove_file parameter specifies if .jsonc file will be removed (deleted from hard drive) after conversion. If set to True, this function will delete .jsonc file leaving only .json file. Otherwise, both files are not deleted. This function can raise _[FunctionParameterError](#exc-function-parameter-error)_ if _filepath_ parameter is not a path-like object or is empty or if _remove_file_ parameter is not a boolean.

-   ##### JsoncParser.convert_to_jsonc(filepath: PathLike, remove_file: bool = False) -> None
    This function converts file from .json to .jsonc format, enabling comment support. filepath parameter specifies path to file and _remove_file_ parameter specifies if .jsonc file will be removed (deleted from hard drive) after conversion. If set to True, this function will delete .jsonc file leaving only .json file. Otherwise, both files are not deleted.
    This function can raise _[FunctionParameterError](#exc-function-parameter-error)_ if _filepath_ parameter is not a path-like object or is empty or if _remove_file_ parameter is not a boolean.

## Exceptions

There are a total of 3 custom exceptions that jsonc-parser can raise during its runtime. To access the in your script, simply import them from jsonc_parser.errors module:

    from jsonc_parser.errors import FileError, IncorrectParameterError, ParserError

#### Exceptions:

-   **FileError**
    <div id='exc-file-error'></div>
    This exception indicates that there is a problem with selected file.

-   **FunctionParameterError**
    <div id='exc-function-parameter-error'></div>
    This exception indicates that some of function's parameters are invalid. They may have wrong type, have invalid values or be erroneous in some other way.

-   **ParserError**
    <div id='exc-parser-error'></div>
    This exception indicates that file cannot be parsed. It can have wrong extension, invalid data, etc.

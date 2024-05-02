#! /usr/bin/env python3

"""
Used to generate python/szerrors.py
"""

import json
import logging
import os
from datetime import datetime, timezone

INPUT_FILE = "szerrors.json"
OUTPUT_FILE = "python/szerrors.py"
PAD_CLASS = 35


def spaces_not_tabs():
    """Because tabs are used in OUTPUT_HEADER, linters get confused with spaces vs. tabs.  This solves it."""


# -----------------------------------------------------------------------------
# --- Main
# -----------------------------------------------------------------------------

# Set up logging.

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

logging.info("-" * 80)
logging.info("--- %s - Begin", os.path.basename(__file__))
logging.info("-" * 80)

# Create multi-line strings for output.

OUTPUT_HEADER = '''#! /usr/bin/env python3
"""
DO NOT EDIT.  This code is generated.
Generated by: sz-sdk-errors/bin/generate_python.py
Generated for: sz-sdk-python/src/senzing/szerrors.py
'''

OUTPUT_HEADER += f"Generated date: {datetime.now(timezone.utc).isoformat()}\n"
OUTPUT_HEADER += '"""'
OUTPUT_HEADER += "\n"

# noqa: E101
OUTPUT_HEADER += '''
import datetime
import json
import threading
import traceback
from ctypes import c_char, create_string_buffer, sizeof
from typing import Any, Callable, Dict

# Metadata

__all__ = [
    "SzBadInputError",
    "SzConfigurationError",
    "SzDatabaseConnectionLostError",
    "SzDatabaseError",
    "SzError",
    "SzLicenseError",
    "SzNotFoundError",
    "SzNotInitializedError",
    "SzRetryableError",
    "SzRetryTimeoutExceededError",
    "SzUnhandledError",
    "SzUnknownDataSourceError",
    "SzUnrecoverableError",
    "new_szexception",
]
__version__ = "0.0.1"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = "2023-10-30"
__updated__ = "2023-10-30"


# -----------------------------------------------------------------------------
# Base SzError
# -----------------------------------------------------------------------------


class SzError(Exception):
    """Base exception for Sz related python code."""


# -----------------------------------------------------------------------------
# Category exceptions
# - These exceptions represent categories of actions that can be taken by
#   the calling program.
# -----------------------------------------------------------------------------


class SzBadInputError(SzError):
    """The user-supplied input contained an error."""


class SzConfigurationError(SzError):
    """The program can provide a remedy and continue."""


class SzRetryableError(SzError):
    """The program can provide a remedy and continue."""


class SzUnrecoverableError(SzError):
    """System failure, can't continue."""


# -----------------------------------------------------------------------------
# Detail exceptions for SzBadInputException
# - Processing did not complete.
# - These exceptions are "per record" exceptions.
# - The record should be recorded as "bad".  (logged, queued as failure)
# - Processing may continue.
# -----------------------------------------------------------------------------


class SzNotFoundError(SzBadInputError):
    """Not found"""


class SzUnknownDataSourceError(SzBadInputError):
    """Unknown DataSource"""


# -----------------------------------------------------------------------------
# Detail exceptions for SzRetryableException
# - Processing did not complete.
# - These exceptions may be remedied programmatically.
# - The call to the Senzing method should be retried.
# - Processing may continue.
# -----------------------------------------------------------------------------


class SzDatabaseConnectionLostError(SzRetryableError):
    """Database connection lost"""


class SzRetryTimeoutExceededError(SzRetryableError):
    """Retry timeout exceeded time limit"""


# -----------------------------------------------------------------------------
# Detail exceptions for SzUnrecoverableException
# - Processing did not complete.
# - These exceptions cannot be remedied programmatically.
# - Processing cannot continue.
# -----------------------------------------------------------------------------


class SzDatabaseError(SzUnrecoverableError):
    """Database exception"""


class SzLicenseError(SzUnrecoverableError):
    """Licence exception"""


class SzNotInitializedError(SzUnrecoverableError):
    """Not initialized"""


class SzUnhandledError(SzUnrecoverableError):
    """Could not handle exception"""


# -----------------------------------------------------------------------------
# Determine Exception based on Senzing reason code.
# Reference: https://senzing.zendesk.com/hc/en-us/articles/360026678133-Engine-Error-codes
# -----------------------------------------------------------------------------

# fmt: off
EXCEPTION_MAP = {
'''  # noqa: E101, W191


OUTPUT_FOOTER = '''}
# fmt: on


# -----------------------------------------------------------------------------
# ErrorBuffer class
# -----------------------------------------------------------------------------


class ErrorBuffer(threading.local):
    """Buffer to call C"""

    # pylint: disable=R0903

    def __init__(self) -> None:
        super().__init__()
        self.string_buffer = create_string_buffer(65535)
        self.string_buffer_size = sizeof(self.string_buffer)


ERROR_BUFFER = ErrorBuffer()
ERROR_BUFFER_TYPE = c_char * 65535


# -----------------------------------------------------------------------------
# Helper functions to create a senzing-specific Exception
# -----------------------------------------------------------------------------


def get_location() -> str:
    """
    Determine caller.

    :meta private:
    """
    stack = traceback.format_stack()
    return stack[0].replace("\\n   ", "", 1).rstrip()


def get_message_level(error_id: int) -> str:
    """
    Determine the severity of the error.

    :meta private:
    """
    error_levels = {
        6000: "PANIC",
        5000: "FATAL",
        4000: "ERROR",
        3000: "WARN",
        2000: "INFO",
        1000: "DEBUG",
        0: "TRACE",
    }
    for error_level, error_message in error_levels.items():
        if error_id > error_level:
            return error_message
    return "PANIC"


def get_message_text(error_id: int, id_messages: Dict[int, str], *args: Any) -> str:
    """
    Format the message text from a template and variables.

    :meta private:
    """
    return id_messages.get(error_id, f"No message for index {error_id}.").format(*args)


def get_senzing_error_code(error_text: str) -> int:
    """
    Given an exception string, find the exception code.

    :meta private:
    """
    if len(error_text) == 0:
        return 0
    exception_message_splits = error_text.split("|", 1)
    try:
        result = int(exception_message_splits[0].strip().rstrip("EIW"))
    except ValueError:
        print("ERROR: Could not parse error text '{error_text}'")
        result = 9999
    return result


def get_senzing_error_text(
    get_last_exception: Callable[[ERROR_BUFFER_TYPE, int], str],  # type: ignore
    clear_last_exception: Callable[[], None],
) -> str:
    """
    Get the last exception from the Senzing engine.

    :meta private:
    """
    get_last_exception(
        ERROR_BUFFER.string_buffer,
        sizeof(ERROR_BUFFER.string_buffer),
    )
    clear_last_exception()
    result = ERROR_BUFFER.string_buffer.value.decode()
    return result


def new_szexception(
    get_last_exception: Callable[[ERROR_BUFFER_TYPE, int], str],  # type: ignore
    clear_last_exception: Callable[[], None],
    product_id: str,
    error_id: int,
    id_messages: Dict[int, str],
    *args: Any,
) -> Exception:
    """
    Generate a new Senzing Exception based on the error_id.

    :meta private:
    """
    senzing_error_text = get_senzing_error_text(
        get_last_exception, clear_last_exception
    )
    senzing_error_code = get_senzing_error_code(senzing_error_text)
    message = {
        "time": datetime.datetime.utcnow().isoformat("T"),
        "text": get_message_text(error_id, id_messages, *args),
        "level": get_message_level(error_id),
        "id": f"senzing-{product_id}{error_id:4d}",
        "location": get_location(),
        "errorCode": senzing_error_code,
        "errorText": senzing_error_text,
        "details": args,
    }
    senzing_error_class = EXCEPTION_MAP.get(senzing_error_code, SzError)
    return senzing_error_class(json.dumps(message))
'''  # noqa: E101,F541,W191

with open(INPUT_FILE, encoding="utf-8") as input_file:
    errors = json.load(input_file)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(OUTPUT_HEADER)
    for error_number, error_data in errors.items():
        OUTPUT_LINE = ""
        error_class = error_data.get("class")
        if error_class:
            OUTPUT_LINE = f"    {error_number}: {error_class},"
            error_name = error_data.get("name")
            error_comment = error_data.get("comment")
            if error_name or error_comment:
                pad_class_len = len(error_number) + len(error_class)
                OUTPUT_LINE += (
                    " " * (PAD_CLASS - pad_class_len)
                ) + f'  # {error_name:<85} "{error_comment}"'
        if len(OUTPUT_LINE) > 0:
            OUTPUT_LINE += "\n"
            file.write(OUTPUT_LINE)
    file.write(OUTPUT_FOOTER)

# Epilog.

logging.info("-" * 80)
logging.info("--- %s} - End", os.path.basename(__file__))
logging.info("-" * 80)

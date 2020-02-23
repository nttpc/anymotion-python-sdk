"""AnyMotion API SDK for Python."""

import logging
from typing import Optional

import pkg_resources

from .client import Client  # noqa: F401
from .exceptions import (  # noqa: F401
    ClientValueError,
    FileTypeError,
    RequestsError,
    ResponseError,
)

__version__ = pkg_resources.get_distribution(__name__).version


def set_stream_logger(
    name: str = __name__, level: int = logging.INFO, format_string: Optional[str] = None
) -> None:
    """Add a stream handler for the given name and level to the logging module."""
    if format_string is None:
        format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


logging.getLogger(__name__).addHandler(logging.NullHandler())

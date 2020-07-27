import base64
import hashlib
import inspect
from functools import wraps
from pathlib import Path

from .exceptions import ClientException, FileTypeError

MOVIE_SUFFIXES = [".mp4", ".mov"]
IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png"]
AVAILABLE_ENDPOINTS = [
    "images",
    "movies",
    "keypoints",
    "drawings",
    "analyses",
    "comparisons",
]


def create_md5(path: Path) -> str:
    """Create MD5 from file."""
    with path.open("rb") as f:
        md5 = hashlib.md5(f.read()).digest()
        encoded_content_md5 = base64.b64encode(md5)
        content_md5 = encoded_content_md5.decode()
    return content_md5


def get_media_type(path: Path) -> str:
    """Get media type."""
    if path.suffix.lower() in MOVIE_SUFFIXES:
        return "movie"
    elif path.suffix.lower() in IMAGE_SUFFIXES:
        return "image"
    else:
        suffix = MOVIE_SUFFIXES + IMAGE_SUFFIXES
        message = (
            f"The extension of the file {path} must be"
            f"{', '.join(suffix[:-1])} or {suffix[-1]}."
        )
        raise FileTypeError(message)


def check_endpoint(func):
    """Check available endpoint."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        args_value = sig.bind(*args, **kwargs)
        endpoint = args_value.arguments["endpoint"]

        if endpoint not in AVAILABLE_ENDPOINTS:
            raise ClientException(f"Unavailable endpoints: {endpoint}")

        return func(*args, **kwargs)

    return wrapper

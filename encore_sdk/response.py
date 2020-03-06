from typing import Any, Optional, Union

import requests


class HttpResponse(object):
    """AnyMotion API Response."""

    def __init__(self, response: requests.Response):
        self.raw = response

    @property
    def json(self) -> Any:
        """Get json data."""
        return self.raw.json()

    # TODO: add default to args
    def get(self, keys: Union[str, tuple]) -> Any:
        """Fetch element from response."""
        if not isinstance(self.json, dict):
            raise ValueError

        if isinstance(keys, str):
            return self.json.get(keys)
        else:
            return (self.json.get(k) for k in keys)


class Result(HttpResponse):
    """Processing result.

    The result of processing by AnyMotion API such as extraction, drawing and analysis.
    """

    def __init__(self, response: requests.Response):
        super().__init__(response)
        self._status = ""

    def __repr__(self):
        return f"<Result [{self._status}]>"

    @property
    def status(self) -> str:
        """Return status."""
        if self._status == "":
            self._status = self.json.get("execStatus")
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def failure_detail(self) -> Optional[str]:
        """Return failure_detail."""
        if self.status == "FAILURE":
            return self.json.get("failureDetail")
        else:
            return None

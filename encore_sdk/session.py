from textwrap import dedent
from typing import Any, Callable, List, Optional

import requests

from .exceptions import RequestsError


class HttpSession(object):
    """Encapsulates a single HTTP request."""

    def __init__(self):
        self.session = requests.Session()
        self.request_callbacks: List[Callable] = []
        self.response_callbacks: List[Callable] = []

    def request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[dict] = None,
        token: str = None,
    ) -> requests.Response:
        """Execute the request.

        Raises:
            RequestsError
        """
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise RequestsError("HTTP method is invalid.")

        headers = headers or {}
        if json:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = requests.Request(
            method, url, params=params, data=data, json=json, headers=headers,
        )
        for callback in self.request_callbacks:
            callback(request)
        prepped = request.prepare()

        try:
            response = self.session.send(prepped)
        except requests.ConnectionError:
            raise RequestsError(f"{method} {url} is failed.")

        for callback in self.response_callbacks:
            callback(response)

        if response.status_code not in [200, 201]:
            # TODO: change message
            message = dedent(
                f"""\
                    {method} {url} is failed.
                    status code: {response.status_code}
                    content: {response.content.decode()}
                """
            )
            raise RequestsError(message)

        return response

    def add_request_callback(self, callback: Callable) -> None:
        """Add request callback."""
        self.request_callbacks.append(callback)

    def add_response_callback(self, callback: Callable) -> None:
        """Add response callback."""
        self.response_callbacks.append(callback)

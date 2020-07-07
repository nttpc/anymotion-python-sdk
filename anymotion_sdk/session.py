from collections import deque
from logging import getLogger
from textwrap import dedent
from typing import Any, Callable, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import RequestsError
from .response import HttpResponse

logger = getLogger(__name__)


class HttpSession(object):
    """Encapsulates a single HTTP request."""

    def __init__(
        self,
        retry_total: int = 5,
        retry_backoff_factor: Union[int, float] = 0.1,
        history_size: int = 10000,
    ):
        self.session = requests.Session()

        retries = Retry(
            total=retry_total,
            backoff_factor=retry_backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.request_histories: deque = deque(maxlen=history_size)
        self.response_histories: deque = deque(maxlen=history_size)

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
    ) -> HttpResponse:
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
        prepped = request.prepare()

        logger.debug(f"Sending http request: {prepped}")
        logger.debug(f"{prepped.method} {prepped.url}")
        logger.debug(f"Request headers: {prepped.headers}")
        logger.debug(f"Request body: {prepped.body!r}")

        self.request_histories.append(request)
        for callback in self.request_callbacks:
            callback(request)

        try:
            response = self.session.send(prepped)
        except requests.ConnectionError:
            self.request_histories.pop()
            raise RequestsError(f"{method} {url} is failed.")

        logger.debug(f"Received http response: {response}")
        logger.debug(f"Response headers: {response.headers}")
        if "binary" not in response.headers.get("Content-Type", ""):
            logger.debug(f"Response body: {response.text}")

        self.response_histories.append(response)
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

        return HttpResponse(response)

    def add_request_callback(self, callback: Callable) -> None:
        """Add request callback."""
        self.request_callbacks.append(callback)

    def add_response_callback(self, callback: Callable) -> None:
        """Add response callback."""
        self.response_callbacks.append(callback)

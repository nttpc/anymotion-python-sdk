import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse, urlunparse

from .auth import get_token
from .exceptions import ClientValueError
from .response import Response
from .session import HttpSession
from .utils import create_md5, get_media_type


class Client(object):
    """API Client for the AnyMotion API.

    Attributes:
        token (str): The access token for authentication.
        session (HttpSession)

    Examples:
        >>> client = Client()
        >>> client.get_one_data("images", 1)
        {'id': 1, 'name': None, 'contentMd5': '/vtARXU7pPhu/8qJaV+Ahw=='}
    """

    def __init__(
        self,
        client_id: str = os.getenv("ANYMOTION_CLIENT_ID", ""),
        client_secret: str = os.getenv("ANYMOTION_CLIENT_SECRET", ""),
        api_url: str = os.getenv(
            "ANYMOTION_API_URL", "https://api.customer.jp/anymotion/v1/"
        ),
        interval: Union[int, float] = 5,
        timeout: Union[int, float] = 600,
    ):
        """Initialize the client.

        Args:
            client_id: The value used for authentication.
            client_secret: The value used for authentication.
            api_url: The AnyMotion API URL to request.
            interval: The request interval time(sec).
            timeout: The request timeout period(sec).

        Note:
            If client_id, client_secret and api_url are not set, the environment
            variables is used.

        Raises
            ClientValueError: Invalid argument value.
        """
        self.session = HttpSession()

        if client_id is None or client_id == "":
            raise ClientValueError(f"Client ID is not set.")
        self.client_id = client_id

        if client_secret is None or client_secret == "":
            raise ClientValueError(f"Client Secret is not set.")
        self.client_secret = client_secret

        parts = urlparse(api_url)
        api_path = parts.path
        if "anymotion" not in api_path:
            raise ClientValueError(f"Invalid API URL: {api_url}")
        if api_path[-1] != "/":
            api_path += "/"

        self._base_url = str(urlunparse((parts.scheme, parts.netloc, "", "", "", "")))
        self._api_url = urljoin(self._base_url, api_path)
        self._token: Optional[str] = None

        self._interval = max(0.1, interval)
        self._max_steps = int(max(1, timeout / self._interval))

        self._page_size = 1000

    @property
    def token(self) -> str:
        """Return access token."""
        if self._token is None:
            self._token = get_token(
                self.client_id,
                self.client_secret,
                base_url=self._base_url,
                session=self.session,
            )
        return self._token

    def get_one_data(self, endpoint: str, endpoint_id: int) -> dict:
        """Get one piece of data from AnyMotion API.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"{endpoint}/{endpoint_id}/")
        response = self.session.request(url, token=self.token)
        return response.json()

    def get_list_data(self, endpoint: str, params: dict = {}) -> List[dict]:
        """Get list data from AnyMotion API.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"{endpoint}/")
        params["size"] = self._page_size
        data: List[dict] = []
        while url:
            response = self.session.request(url, params=params, token=self.token)
            sub_data, url = Response(response).get(("data", "next"))
            data += sub_data
        return data

    def upload(self, path: Union[str, Path]) -> Tuple[int, str]:
        """Upload movie or image to the cloud storage.

        Args:
            path: The path of the file to upload.

        Returns:
            A tuple of media_id and media_type. media_id is the created image_id or
            movie_id. media_type is the string of "image" or "movie".

        Raises:
            FileTypeError: Invalid file types.
            RequestsError: HTTP request fails.
        """
        if isinstance(path, str):
            path = Path(path)

        media_type = get_media_type(path)
        content_md5 = create_md5(path)

        # Register movie or image
        response = self.session.request(
            urljoin(self._api_url, f"{media_type}s/"),
            method="POST",
            json={
                "origin_key": path.name,
                "content_md5": content_md5,
                "name": path.stem,
            },
            token=self.token,
        )
        media_id, upload_url = Response(response).get(("id", "uploadUrl"))

        # Upload to the cloud storage
        self.session.request(
            upload_url,
            method="PUT",
            data=path.open("rb"),
            headers={"Content-MD5": content_md5},
        )

        return media_id, media_type

    def download(self, drawing_id: int, path: Path) -> None:
        """Download file from drawing_id.

        Args:
            drawing_id
            path: output path.

        Raises:
            RequestsError: HTTP request fails.
        """
        # TODO: not exists path check
        data = self.get_one_data("drawings", drawing_id)
        url = data.get("drawingUrl")
        if url is None:
            # TODO: add message
            return

        response = self.session.request(url)
        with path.open("wb") as f:
            f.write(response.content)

    def extract_keypoint(
        self,
        data: Optional[dict] = None,
        image_id: Optional[int] = None,
        movie_id: Optional[int] = None,
    ) -> int:
        """Start keypoint extraction.

        Args:
            image_id
            movie_id
            data: example: {"image_id": 1} or {"movie_id: 2}

        Note:
            One of movie_id, image_id or data is required.

        Returns:
            keypoint_id.

        Raises:
            ValueError: Invalid argument.
            RequestsError: HTTP request fails.
        """
        if [movie_id, image_id, data].count(None) != 2:
            raise ValueError("One of movie_id, image_id or data is required.")

        if movie_id:
            data = {"movie_id": movie_id}
        if image_id:
            data = {"image_id": image_id}

        url = urljoin(self._api_url, "keypoints/")
        response = self.session.request(url, method="POST", json=data, token=self.token)
        (keypoint_id,) = Response(response).get("id")
        return keypoint_id

    def draw_keypoint(
        self, keypoint_id: int, rule: Optional[Union[list, dict]] = None
    ) -> int:
        """Start drawing for keypoint_id.

        Returns:
            drawing_id.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"drawings/")
        json: Dict[str, Union[int, list, dict]] = {"keypoint_id": keypoint_id}
        if rule is not None:
            json["rule"] = rule
        response = self.session.request(url, method="POST", json=json, token=self.token)
        (drawing_id,) = Response(response).get("id")
        return drawing_id

    def analyze_keypoint(self, keypoint_id: int, rule: Union[list, dict]) -> int:
        """Start analyze for keypoint_id.

        Returns:
            analysis_id.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"analyses/")
        json: Dict[str, Union[int, list, dict]] = {"keypoint_id": keypoint_id}
        if rule is not None:
            json["rule"] = rule
        response = self.session.request(url, method="POST", json=json, token=self.token)
        (analysis_id,) = Response(response).get("id")
        return analysis_id

    def wait_for_extraction(self, keypoint_id: int) -> Response:
        """Wait for extraction.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"keypoints/{keypoint_id}/")
        response = self._wait_for_done(url)
        return response

    def wait_for_drawing(self, drawing_id: int) -> Response:
        """Wait for drawing.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"drawings/{drawing_id}/")
        response = self._wait_for_done(url)
        return response

    def wait_for_analysis(self, analysis_id: int) -> Response:
        """Wait for analysis.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"analyses/{analysis_id}/")
        response = self._wait_for_done(url)
        return response

    def _wait_for_done(self, url: str) -> Response:
        for _ in range(self._max_steps):
            response = Response(self.session.request(url, token=self.token))
            if response.status in ["SUCCESS", "FAILURE"]:
                break
            time.sleep(self._interval)
        else:
            response.status = "TIMEOUT"
        return response

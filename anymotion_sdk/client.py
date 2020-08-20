import os
import time
from collections import namedtuple
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse, urlunparse

from .auth import Authentication
from .exceptions import ClientException, ClientValueError, ExtraPackageError
from .response import Result
from .session import HttpSession
from .utils import check_endpoint, create_md5, get_media_type

logger = getLogger(__name__)
UploadResult = namedtuple("UploadResult", ("image_id", "movie_id"))


class Client(object):
    """API Client for the AnyMotion API.

    Attributes:
        token (str): The access token for authentication.
        session (HttpSession)

    Examples:
        >>> client = Client()
        >>> client.get_image(1)
        {'id': 1, 'name': 'sample', 'contentMd5': '/vtARXU7pPhu/8qJaV+Ahw=='}
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
        session: HttpSession = HttpSession(),
    ):
        """Initialize the client.

        Args:
            client_id: The value used for authentication.
            client_secret: The value used for authentication.
            api_url: The AnyMotion API URL to request.
            interval: The request interval time(sec).
            timeout: The request timeout period(sec).

        Note:
            If client_id, client_secret, and api_url are not set, environment
            variables "ANYMOTION_CLIENT_ID", "ANYMOTION_CLIENT_SECRET", and
            "ANYMOTION_API_URL" are used, respectively.
            In addition, if ANYMOTION_API_URL is not set, the default value
            "https://api.customer.jp/anymotion/v1/" is used.

        Raises
            ClientValueError: Invalid argument value.
        """
        logger.debug("Initializing client.")

        if not isinstance(session, HttpSession):
            raise ClientValueError(
                f"session is must be HttpSession class: {type(session)}"
            )
        self.session = session

        parts = urlparse(api_url)
        api_path = parts.path
        if "anymotion" not in api_path:
            raise ClientValueError(f"Invalid API URL: {api_url}")
        if api_path[-1] != "/":
            api_path += "/"

        base_url = str(urlunparse((parts.scheme, parts.netloc, "", "", "", "")))
        self._api_url = urljoin(base_url, api_path)

        self.auth = Authentication(
            client_id, client_secret, base_url=base_url, session=self.session
        )

        self._interval = max(0.1, interval)
        self._max_steps = int(max(1, timeout / self._interval))

        self._page_size = 1000

    @check_endpoint
    def get_one_data(self, endpoint: str, endpoint_id: int) -> dict:
        """Get one piece of data.

        Args:
            endpoint: images, movies, keypoints, drawings, analyses, or comparisons
            endpoint_id

        Returns:
            API response data.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"{endpoint}/{endpoint_id}/")
        response = self.session.request(url, token=self.auth.token)
        return response.json

    def get_image(self, image_id: int) -> dict:
        """Get image data."""
        return self.get_one_data("images", image_id)

    def get_movie(self, movie_id: int) -> dict:
        """Get movie data."""
        return self.get_one_data("movies", movie_id)

    def get_keypoint(self, keypoint_id: int, join_data: bool = False) -> dict:
        """Get keypoint data."""
        keypoint = self.get_one_data("keypoints", keypoint_id)
        if join_data:
            image_id = keypoint.get("image")
            if image_id:
                keypoint["image"] = self.get_image(image_id)
            movie_id = keypoint.get("movie")
            if movie_id:
                keypoint["movie"] = self.get_movie(movie_id)
        return keypoint

    def get_drawing(self, drawing_id: int, join_data: bool = False) -> dict:
        """Get drawing data."""
        drawing = self.get_one_data("drawings", drawing_id)
        if join_data:
            keypoint_id = drawing.get("keypoint")
            if keypoint_id:
                drawing["keypoint"] = self.get_keypoint(keypoint_id, join_data=True)
        return drawing

    def get_analysis(self, analysis_id: int, join_data: bool = False) -> dict:
        """Get analysis data."""
        analysis = self.get_one_data("analyses", analysis_id)
        if join_data:
            keypoint_id = analysis.get("keypoint")
            if keypoint_id:
                analysis["keypoint"] = self.get_keypoint(keypoint_id, join_data=True)
        return analysis

    def get_comparison(self, comparison_id: int, join_data: bool = False) -> dict:
        """Get comparisons data."""
        comparison = self.get_one_data("comparisons", comparison_id)
        if join_data:
            source_keypoint_id = comparison.get("source")
            target_keypoint_id = comparison.get("target")
            if source_keypoint_id:
                comparison["source"] = self.get_keypoint(
                    source_keypoint_id, join_data=True
                )
            if target_keypoint_id:
                comparison["target"] = self.get_keypoint(
                    target_keypoint_id, join_data=True
                )
        return comparison

    @check_endpoint
    def get_list_data(self, endpoint: str, params: dict = {}) -> List[dict]:
        """Get list data.

        Args:
            endpoint: images, movies, keypoints, drawings, analyses, or comparisons
            endpoint_id
            params

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"{endpoint}/")
        params["size"] = self._page_size
        data: List[dict] = []
        while url:
            response = self.session.request(url, params=params, token=self.auth.token)
            sub_data, url = response.get(("data", "next"))
            params = {}
            data += sub_data
        return data

    def get_images(self, params: dict = {}) -> List[dict]:
        """Get image list."""
        return self.get_list_data("images", params=params)

    def get_movies(self, params: dict = {}) -> List[dict]:
        """Get movie list."""
        return self.get_list_data("movies", params=params)

    def get_keypoints(self, params: dict = {}) -> List[dict]:
        """Get keypoint list."""
        return self.get_list_data("keypoints", params=params)

    def get_drawings(self, params: dict = {}) -> List[dict]:
        """Get drawing list."""
        return self.get_list_data("drawings", params=params)

    def get_analyses(self, params: dict = {}) -> List[dict]:
        """Get analysis list."""
        return self.get_list_data("analyses", params=params)

    def get_comparisons(self, params: dict = {}) -> List[dict]:
        """Get comparisons list."""
        return self.get_list_data("comparisons", params=params)

    def upload(
        self, path: Union[str, Path], text: Optional[str] = None
    ) -> UploadResult:
        """Upload movie or image to the cloud storage.

        Args:
            path: The path of the file to upload.
            text: The text about this file.

        Returns:
            A tuple of media_id and media_type. media_id is the created image_id or
            movie_id. media_type is the string of "image" or "movie".

        Raises:
            FileNotFoundError: No such file
            FileTypeError: Invalid file types.
            RequestsError: HTTP request fails.
        """
        if isinstance(path, str):
            path = Path(path)
        path = path.expanduser()

        media_type = get_media_type(path)
        content_md5 = create_md5(path)

        # Register movie or image
        response = self.session.request(
            urljoin(self._api_url, f"{media_type}s/"),
            method="POST",
            json={"content_md5": content_md5, "name": path.stem, "text": text},
            token=self.auth.token,
        )
        media_id, upload_url = response.get(("id", "uploadUrl"))

        # Upload to the cloud storage
        self.session.request(
            upload_url,
            method="PUT",
            data=path.open("rb"),
            headers={"Content-MD5": content_md5},
        )

        if media_type == "image":
            return UploadResult(image_id=media_id, movie_id=None)
        else:
            return UploadResult(image_id=None, movie_id=media_id)

    def download(
        self,
        drawing_id: int,
        path: Optional[Union[str, Path]] = None,
        exist_ok: bool = False,
        fix_suffix: bool = False,
    ) -> Path:
        """Download a file from drawing_id.

        Args:
            drawing_id
            path: output file path or directory path.
            exist_ok: if false (default), FileExistsError is raised if the target file
                already exists.
            fix_suffix: If the extension of path is invalid, correct it.

        Returns:
            The path to the downloaded file.

        Raises:
            ClientException
            FileExistsError
            RequestsError: HTTP request fails.
        """
        data = self.get_one_data("drawings", drawing_id)
        url = data.get("drawingUrl")
        if url is None:
            raise ClientException(
                "Can't download the file because it doesn't have a drawing url."
            )
        url_path = Path(urlparse(url).path)

        if path is None:
            path = url_path.name
        if isinstance(path, str):
            path = Path(path)
        path = path.expanduser()

        if path.is_dir():
            path /= url_path.name

        suffix = url_path.suffix
        if fix_suffix and path.suffix != suffix:
            path = path.with_suffix(suffix)
            logger.info(f"Change path to {path}.")

        if path.exists() and not exist_ok:
            logger.error(f"File exists: {path}")
            raise FileExistsError(f"File exists: {path}")

        response = self.session.request(url)
        with path.open("wb") as f:
            f.write(response.raw.content)
        logger.info(f"Download file to {path}.")

        return path

    def download_and_read(self, drawing_id: int):
        """Download and read a file from drawing_id."""
        try:
            from .extras import read_image, read_video
        except ImportError:
            raise ExtraPackageError(
                "The extras package is not installed. "
                "Install as follows: pip install anymotion-sdk[cv]"
            )

        with TemporaryDirectory() as dir_path:
            file_path = self.download(drawing_id, path=dir_path)
            if get_media_type(file_path) == "image":
                return read_image(file_path)
            else:
                return read_video(file_path)

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
        response = self.session.request(
            url, method="POST", json=data, token=self.auth.token
        )
        return response.get("id")

    def draw_keypoint(
        self,
        keypoint_id: Optional[int] = None,
        comparison_id: Optional[int] = None,
        rule: Optional[Union[list, dict]] = None,
        background_rule: Optional[dict] = None,
    ) -> int:
        """Start drawing for keypoint_id or comparison_id.

        Args:
            keypoint_id: Keypoint ID used for drawing.
            comparison_id: Comparison ID used for drawing.
            rule: Rules for how to draw.
                example: {
                    "drawingType": "stickPicture",
                    "pattern": "all",
                    "color": "red"
                }
            background_rule: Rules for what kind of background to draw.
                example: {"skeletonOnly": True}

        Returns:
            drawing_id.

        Raises:
            RequestsError: HTTP request fails.
        """
        if [keypoint_id, comparison_id].count(None) != 1:
            raise ValueError("Either keypoint_id or comparison_id is required.")

        url = urljoin(self._api_url, "drawings/")
        json: Dict[str, Union[int, list, dict]] = {}
        if keypoint_id is not None:
            json["keypoint_id"] = keypoint_id
        if comparison_id is not None:
            json["comparison_id"] = comparison_id
        if rule is not None:
            json["rule"] = rule
        if background_rule is not None:
            json["background_rule"] = background_rule
        response = self.session.request(
            url, method="POST", json=json, token=self.auth.token
        )
        return response.get("id")

    def analyze_keypoint(self, keypoint_id: int, rule: Union[list, dict]) -> int:
        """Start analyze for keypoint_id.

        Returns:
            analysis_id.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, "analyses/")
        json: Dict[str, Union[int, list, dict]] = {"keypoint_id": keypoint_id}
        if rule is not None:
            json["rule"] = rule
        response = self.session.request(
            url, method="POST", json=json, token=self.auth.token
        )
        return response.get("id")

    def compare_keypoint(self, source_id: int, target_id: int) -> int:
        """Start compare for source_id and target_id.

        Args:
            source_id: The keypoint id of the comparison source.
            target_id: The keypoint id of the comparison target.

        Returns:
            comparison_id.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, "comparisons/")
        json = {"source_id": source_id, "target_id": target_id}
        response = self.session.request(
            url, method="POST", json=json, token=self.auth.token
        )
        return response.get("id")

    def wait_for_extraction(self, keypoint_id: int) -> Result:
        """Wait for extraction.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"keypoints/{keypoint_id}/")
        return self._wait_for_done(url)

    def wait_for_drawing(self, drawing_id: int) -> Result:
        """Wait for drawing.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"drawings/{drawing_id}/")
        return self._wait_for_done(url)

    def wait_for_analysis(self, analysis_id: int) -> Result:
        """Wait for analysis.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"analyses/{analysis_id}/")
        return self._wait_for_done(url)

    def wait_for_comparison(self, comparison_id: int) -> Result:
        """Wait for comparison.

        Raises:
            RequestsError: HTTP request fails.
        """
        url = urljoin(self._api_url, f"comparisons/{comparison_id}/")
        return self._wait_for_done(url)

    def _wait_for_done(self, url: str) -> Result:
        for _ in range(self._max_steps):
            response = self.session.request(url, token=self.auth.token)
            result = Result(response.raw)
            if result.status in ["SUCCESS", "FAILURE"]:
                break
            time.sleep(self._interval)
        else:
            result.status = "TIMEOUT"
        return result

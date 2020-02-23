from urllib.parse import urljoin

import pytest

from encore_sdk.client import Client
from encore_sdk.exceptions import ClientValueError, FileTypeError


@pytest.fixture
def make_client(requests_mock):
    def _make_client(
        client_id="client_id",
        client_secret="client_secret",
        api_url="http://api.example.com/anymotion/v1/",
        interval=5,
        timeout=600,
    ):
        client = Client("client_id", "client_secret", api_url, interval, timeout)
        oauth_url = urljoin(client._base_url, "v1/oauth/accesstokens")
        requests_mock.post(oauth_url, json={"accessToken": "token"})
        return client

    return _make_client


class TestInit(object):
    @pytest.mark.parametrize(
        "api_url",
        ["http://api.example.com/anymotion/v1/", "http://api.example.com/anymotion/v1"],
    )
    def test_valid(self, make_client, api_url):
        client = make_client(api_url=api_url)

        assert isinstance(client, Client)
        assert client._api_url == "http://api.example.com/anymotion/v1/"

    @pytest.mark.parametrize(
        "client_id, client_secret, api_url, expected",
        [
            ("", "", "", "Client ID is not set."),
            ("client_id", "", "", "Client Secret is not set."),
            ("client_id", "client_secret", "", "Invalid API URL: "),
            (
                "client_id",
                "client_secret",
                "http://api.example.com/",
                "Invalid API URL: http://api.example.com/",
            ),
        ],
    )
    def test_invalid(self, client_id, client_secret, api_url, expected):
        with pytest.raises(ClientValueError) as excinfo:
            Client(client_id, client_secret, api_url)

        assert str(excinfo.value) == expected


class TestGetData(object):
    def test_get_one_data(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "name": "image"}
        requests_mock.get(
            f"{client._api_url}images/1/", json=data,
        )
        result = client.get_one_data("images", 1)

        assert result == data

    def test_get_image(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "name": "image"}
        requests_mock.get(
            f"{client._api_url}images/1/", json=data,
        )
        result = client.get_image(1)

        assert result == data

    def test_get_movie(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "name": "movie"}
        requests_mock.get(
            f"{client._api_url}movies/1/", json=data,
        )
        result = client.get_movie(1)

        assert result == data

    def test_get_list_data(self, requests_mock, make_client):
        client = make_client()
        data = [{"id": 1, "name": "image"}, {"id": 2, "name": "image"}]
        requests_mock.get(
            f"{client._api_url}images/",
            json={"next": None, "previous": None, "maxPage": 1, "data": data},
        )
        result = client.get_list_data("images")

        assert result == data

    def test_get_images(self, requests_mock, make_client):
        client = make_client()
        data = [{"id": 1, "name": "image"}, {"id": 2, "name": "image"}]
        requests_mock.get(
            f"{client._api_url}images/",
            json={"next": None, "previous": None, "maxPage": 1, "data": data},
        )
        result = client.get_images()

        assert result == data

    def test_get_movies(self, requests_mock, make_client):
        client = make_client()
        data = [{"id": 1, "name": "movie"}, {"id": 2, "name": "movie"}]
        requests_mock.get(
            f"{client._api_url}movies/",
            json={"next": None, "previous": None, "maxPage": 1, "data": data},
        )
        result = client.get_movies()

        assert result == data


class TestUpload(object):
    @pytest.mark.parametrize(
        "expected_media_type, path",
        [
            ("image", "image.jpg"),
            ("image", "image.JPG"),
            ("image", "image.jpeg"),
            ("image", "image.png"),
            ("movie", "movie.mp4"),
            ("movie", "movie.MP4"),
            ("movie", "movie.mov"),
        ],
    )
    def test_ファイルをアップロードできること(
        self, mocker, requests_mock, make_client, expected_media_type, path
    ):
        client = make_client()

        expected_media_id = 1
        upload_url = "http://upload_url.example.com"

        file_mock = mocker.mock_open(read_data=b"image data")
        mocker.patch("pathlib.Path.open", file_mock)
        requests_mock.post(
            urljoin(client._api_url, f"{expected_media_type}s/"),
            json={"id": expected_media_id, "uploadUrl": upload_url},
        )
        requests_mock.put(upload_url)

        result = client.upload(path)

        if expected_media_type == "image":
            assert result.image_id == expected_media_id
            assert result.movie_id is None
        else:
            assert result.image_id is None
            assert result.movie_id == expected_media_id

    def test_正しい拡張子でない場合アップロードできないこと(self, make_client):
        client = make_client()
        path = "test.text"

        with pytest.raises(FileTypeError):
            client.upload(path)


class TestExtractKeypoint(object):
    def test_画像からキーポイント抽出を開始できること(self, requests_mock, make_client):
        client = make_client()
        image_id = 111
        expected_keypoint_id = 222
        requests_mock.post(
            urljoin(client._api_url, "keypoints/"), json={"id": expected_keypoint_id}
        )

        keypoint_id = client.extract_keypoint(image_id=image_id)

        assert keypoint_id == expected_keypoint_id

    def test_dictを使用して画像からキーポイント抽出を開始できること(self, requests_mock, make_client):
        client = make_client()
        image_id = 111
        expected_keypoint_id = 222
        requests_mock.post(
            urljoin(client._api_url, "keypoints/"), json={"id": expected_keypoint_id}
        )

        data = {"image_id": image_id}
        keypoint_id = client.extract_keypoint(data)

        assert keypoint_id == expected_keypoint_id

    def test_動画からキーポイント抽出を開始できること(self, requests_mock, make_client):
        client = make_client()
        movie_id = 111
        expected_keypoint_id = 222
        requests_mock.post(
            urljoin(client._api_url, "keypoints/"), json={"id": expected_keypoint_id}
        )

        keypoint_id = client.extract_keypoint(movie_id=movie_id)

        assert keypoint_id == expected_keypoint_id

    @pytest.mark.parametrize("args", [{}, {"image_id": 1, "movie_id": 2}])
    def test_invalid_argument(self, requests_mock, make_client, args):
        client = make_client()

        with pytest.raises(ValueError) as excinfo:
            client.extract_keypoint(**args)

        assert str(excinfo.value) == "One of movie_id, image_id or data is required."

    def test_キーポイント抽出を完了できること(self, requests_mock, make_client):
        client = make_client()
        keypoint_id = 1
        requests_mock.get(
            urljoin(client._api_url, f"keypoints/{keypoint_id}/"),
            json={"execStatus": "SUCCESS"},
        )

        response = client.wait_for_extraction(keypoint_id)

        assert response.status == "SUCCESS"


class TestDrawingKeypoint(object):
    def test_キーポイント描画を開始できること(self, requests_mock, make_client):
        client = make_client()
        keypoint_id = 1
        expected_drawing_id = 1
        requests_mock.post(
            f"{client._api_url}drawings/", json={"id": expected_drawing_id}
        )

        drawing_id = client.draw_keypoint(keypoint_id)

        assert drawing_id == expected_drawing_id

    def test_キーポイント描画を完了できること(self, requests_mock, make_client):
        client = make_client()
        drawing_id = 1
        expected_drawing_url = "http://drawing_url.example.com"
        requests_mock.get(
            f"{client._api_url}drawings/{drawing_id}/",
            json={"execStatus": "SUCCESS", "drawingUrl": expected_drawing_url},
        )

        response = client.wait_for_drawing(drawing_id)
        drawing_url = response.get("drawingUrl")

        assert response.status == "SUCCESS"
        assert drawing_url == expected_drawing_url


class TestAnalysisKeypoint(object):
    def test_キーポイント解析を開始できること(self, requests_mock, make_client):
        client = make_client()
        keypoint_id = 111
        expected_analysis_id = 222
        rule = []
        requests_mock.post(
            f"{client._api_url}analyses/", json={"id": expected_analysis_id}
        )

        analysis_id = client.analyze_keypoint(keypoint_id, rule)

        assert analysis_id == expected_analysis_id

    def test_キーポイント解析を完了できること(self, requests_mock, make_client):
        client = make_client()
        analysis_id = 222
        requests_mock.get(
            f"{client._api_url}analyses/{analysis_id}/",
            json={"execStatus": "SUCCESS", "result": "[]"},
        )

        response = client.wait_for_analysis(analysis_id)

        assert response.status == "SUCCESS"


class TestDownload(object):
    def test_download_ok(self, tmp_path, requests_mock, make_client):
        client = make_client()
        drawing_id = 111
        url = "http://download.example.com/image.jpg"
        path = tmp_path / "image.jpg"

        requests_mock.get(
            f"{client._api_url}drawings/{drawing_id}/",
            json={"execStatus": "SUCCESS", "drawingUrl": url},
        )
        requests_mock.get(url, content=b"image data")

        assert not path.exists()

        client.download(drawing_id, path)

        assert path.exists()

    def test_download_skip(self, tmp_path, requests_mock, make_client):
        client = make_client()
        drawing_id = 111
        url = "http://download.example.com/image.jpg"
        path = tmp_path / "image.jpg"

        requests_mock.get(
            f"{client._api_url}drawings/{drawing_id}/",
            json={"execStatus": "FAILURE", "drawingUrl": None},
        )
        requests_mock.get(url, content=b"image data")

        assert not path.exists()

        client.download(drawing_id, path)

        assert not path.exists()


class TestWaitForDone(object):
    @pytest.mark.parametrize(
        "response_list, expected",
        [
            ([{"json": {"execStatus": "SUCCESS"}}], "SUCCESS"),
            (
                [
                    {"json": {"execStatus": "PROCESSING"}},
                    {"json": {"execStatus": "SUCCESS"}},
                ],
                "SUCCESS",
            ),
            ([{"json": {"execStatus": "FAILURE"}}], "FAILURE"),
        ],
    )
    def test_success_or_failure(
        self, make_client, requests_mock, response_list, expected
    ):
        url = "https://example.com/"
        client = make_client(interval=0.1)
        requests_mock.register_uri("GET", url, response_list)

        response = client._wait_for_done(url)

        assert response.status == expected

        # NOTE: +1 is POST https://api.example.com/v1/oauth/accesstokens
        assert requests_mock.call_count == len(response_list) + 1

    def test_timeout(self, make_client, requests_mock):
        url = "https://example.com/"
        client = make_client(interval=0.1, timeout=0.1)
        requests_mock.register_uri(
            "GET",
            url,
            [
                {"json": {"execStatus": "PROCESSING"}},
                {"json": {"execStatus": "SUCCESS"}},
            ],
        )

        response = client._wait_for_done(url)

        assert response.status == "TIMEOUT"
        assert requests_mock.call_count == 2

from urllib.parse import urljoin

import numpy as np
import pytest

from anymotion_sdk.client import Client
from anymotion_sdk.exceptions import ClientException, ClientValueError, FileTypeError
from anymotion_sdk.session import HttpSession


@pytest.fixture
def make_client(mocker):
    def _make_client(
        client_id="client_id",
        client_secret="client_secret",
        api_url="http://api.example.com/anymotion/v1/",
        interval=5,
        timeout=600,
        session=None,
    ):
        if session is None:
            session = HttpSession()
        client = Client(client_id, client_secret, api_url, interval, timeout, session)
        auth_mock = mocker.MagicMock()
        auth_mock.token = "token"
        mocker.patch.object(client, "auth", auth_mock)
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
        "args, expected",
        [
            ({"client_id": ""}, "Client ID is not set."),
            ({"client_secret": ""}, "Client Secret is not set."),
            ({"api_url": ""}, "Invalid API URL: "),
            (
                {"api_url": "http://api.example.com/"},
                "Invalid API URL: http://api.example.com/",
            ),
            ({"session": ""}, "session is must be HttpSession class: <class 'str'>"),
        ],
    )
    def test_invalid(self, make_client, args, expected):
        with pytest.raises(ClientValueError) as excinfo:
            make_client(**args)

        assert str(excinfo.value) == expected


class TestGetData(object):
    def test_get_one_data(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "name": "image"}
        requests_mock.get(
            f"{client._api_url}images/1/",
            json=data,
        )
        result = client.get_one_data("images", 1)

        assert result == data

    def test_get_image(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "name": "image"}
        requests_mock.get(
            f"{client._api_url}images/1/",
            json=data,
        )
        result = client.get_image(1)

        assert result == data

    def test_get_movie(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "name": "movie"}
        requests_mock.get(
            f"{client._api_url}movies/1/",
            json=data,
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


class TestGetKeypoint(object):
    def test_without_join_data(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "image": 2, "movie": None, "keypoint": [{"nose": [10, 20]}]}
        requests_mock.get(
            f"{client._api_url}keypoints/1/",
            json=data,
        )
        result = client.get_keypoint(1)

        assert result == data

    def test_with_join_image_data(self, requests_mock, make_client):
        client = make_client()
        keypoint = {
            "id": 1,
            "image": 2,
            "movie": None,
            "keypoint": [{"nose": [10, 20]}],
        }
        image = {"id": 2, "name": "image"}
        requests_mock.get(
            f"{client._api_url}keypoints/1/",
            json=keypoint,
        )
        requests_mock.get(
            f"{client._api_url}images/2/",
            json=image,
        )
        result = client.get_keypoint(1, join_data=True)

        expected = keypoint
        expected["image"] = image
        assert result == expected

    def test_with_join_movie_data(self, requests_mock, make_client):
        client = make_client()
        keypoint = {
            "id": 1,
            "image": None,
            "movie": 2,
            "keypoint": [{"nose": [10, 20]}],
        }
        movie = {"id": 2, "name": "movie"}
        requests_mock.get(
            f"{client._api_url}keypoints/1/",
            json=keypoint,
        )
        requests_mock.get(
            f"{client._api_url}movies/2/",
            json=movie,
        )
        result = client.get_keypoint(1, join_data=True)

        expected = keypoint
        expected["movie"] = movie
        assert result == expected


class TestGetDrawing(object):
    def test_without_join_data(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "keypoint": 2}
        requests_mock.get(
            f"{client._api_url}drawings/1/",
            json=data,
        )
        result = client.get_drawing(1)

        assert result == data

    def test_with_join_data(self, requests_mock, make_client):
        client = make_client()
        drawing = {"id": 1, "keypoint": 2}
        keypoint = {
            "id": 2,
            "image": 3,
            "movie": None,
            "keypoint": [{"nose": [10, 20]}],
        }
        image = {"id": 3, "name": "image"}
        requests_mock.get(
            f"{client._api_url}drawings/1/",
            json=drawing,
        )
        requests_mock.get(
            f"{client._api_url}keypoints/2/",
            json=keypoint,
        )
        requests_mock.get(
            f"{client._api_url}images/3/",
            json=image,
        )
        result = client.get_drawing(1, join_data=True)

        expected = drawing
        expected["keypoint"] = keypoint
        expected["keypoint"]["image"] = image
        assert result == expected


class TestGetAnalysis(object):
    def test_without_join_data(self, requests_mock, make_client):
        client = make_client()
        data = {"id": 1, "keypoint": 2}
        requests_mock.get(
            f"{client._api_url}analyses/1/",
            json=data,
        )
        result = client.get_analysis(1)

        assert result == data

    def test_with_join_data(self, requests_mock, make_client):
        client = make_client()
        analysis = {"id": 1, "keypoint": 2}
        keypoint = {
            "id": 2,
            "image": 3,
            "movie": None,
            "keypoint": [{"nose": [10, 20]}],
        }
        image = {"id": 3, "name": "image"}
        requests_mock.get(
            f"{client._api_url}analyses/1/",
            json=analysis,
        )
        requests_mock.get(
            f"{client._api_url}keypoints/2/",
            json=keypoint,
        )
        requests_mock.get(
            f"{client._api_url}images/3/",
            json=image,
        )
        result = client.get_analysis(1, join_data=True)

        expected = analysis
        expected["keypoint"] = keypoint
        expected["keypoint"]["image"] = image
        assert result == expected


class TestGetComparison(object):
    def test_without_join_data(self, requests_mock, make_client):
        client = make_client()
        comparison = {"id": 1, "source": 2, "target": 3}
        requests_mock.get(
            f"{client._api_url}comparisons/1/",
            json=comparison,
        )
        result = client.get_comparison(1)

        assert result == comparison

    def test_with_join_data(self, requests_mock, make_client):
        client = make_client()
        comparison = {"id": 1, "source": 2, "target": 3}
        source = {
            "id": 2,
            "image": 3,
            "movie": None,
            "keypoint": [{"nose": [10, 20]}],
        }
        target = {
            "id": 3,
            "image": 3,
            "movie": None,
            "keypoint": [{"nose": [10, 20]}],
        }
        image = {"id": 3, "name": "image"}
        requests_mock.get(f"{client._api_url}comparisons/1/", json=comparison)
        requests_mock.get(f"{client._api_url}keypoints/2/", json=source)
        requests_mock.get(f"{client._api_url}keypoints/3/", json=target)
        requests_mock.get(f"{client._api_url}images/3/", json=image)

        result = client.get_comparison(1, join_data=True)

        expected = comparison
        expected["source"] = source
        expected["source"]["image"] = image
        expected["target"] = target
        expected["target"]["image"] = image
        assert result == expected


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


class TestDrawKeypoint(object):
    @pytest.mark.parametrize(
        "id_kwargs", [{"keypoint_id": 111}, {"comparison_id": 111}]
    )
    @pytest.mark.parametrize(
        "rule_kwargs",
        [
            {},
            {
                "rule": {
                    "drawing_type": "stickPicture",
                    "pattern": "all",
                    "color": "red",
                },
            },
        ],
    )
    @pytest.mark.parametrize(
        "bgrule_kwargs",
        [{}, {"background_rule": {"skeletonOnly": True}}],
    )
    def test_can_start_keypoint_drawing(
        self, requests_mock, make_client, id_kwargs, rule_kwargs, bgrule_kwargs
    ):
        client = make_client()
        expected_drawing_id = 222
        requests_mock.post(
            f"{client._api_url}drawings/", json={"id": expected_drawing_id}
        )

        kwargs = dict(id_kwargs, **rule_kwargs, **bgrule_kwargs)
        drawing_id = client.draw_keypoint(**kwargs)

        assert drawing_id == expected_drawing_id

    @pytest.mark.parametrize("kwargs", [{}, {"keypoint_id": 111, "comparison_id": 111}])
    def test_can_not_start_keypoint_drawing(self, requests_mock, make_client, kwargs):
        expected = "Either keypoint_id or comparison_id is required."
        client = make_client()

        with pytest.raises(ValueError) as excinfo:
            client.draw_keypoint(**kwargs)

        assert str(excinfo.value) == expected

    def test_can_complete_keypoint_drawing(self, requests_mock, make_client):
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


class TestAnalyzeKeypoint(object):
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


class TestComapreKeypoint(object):
    def test_can_start_keypoint_comparison(self, requests_mock, make_client):
        client = make_client()
        source_id = 111
        target_id = 222
        expected_comparison_id = 333
        requests_mock.post(
            f"{client._api_url}comparisons/", json={"id": expected_comparison_id}
        )

        comparison_id = client.compare_keypoint(source_id, target_id)

        assert comparison_id == expected_comparison_id

    def test_can_complete_keypoint_drawing(self, requests_mock, make_client):
        client = make_client()
        comparison_id = 333
        requests_mock.get(
            f"{client._api_url}comparisons/{comparison_id}/",
            json={"execStatus": "SUCCESS"},
        )

        response = client.wait_for_comparison(comparison_id)

        assert response.status == "SUCCESS"


class TestDownload(object):
    def test_valid_path(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client)

        path = tmp_path / "image.jpg"
        expected_path = path

        assert not expected_path.exists()

        client.download(111, path)

        assert expected_path.exists()
        assert expected_path.read_bytes() == b"image data"

    def test_str_path(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client)

        path = tmp_path / "image.jpg"
        expected_path = path

        assert not expected_path.exists()

        client.download(111, str(path))

        assert expected_path.exists()
        assert expected_path.read_bytes() == b"image data"

    def test_no_path(self, tmp_path, monkeypatch, requests_mock, make_client, setup):
        monkeypatch.chdir(tmp_path)
        client = make_client()
        setup(client)

        expected_path = tmp_path / "image.jpg"

        assert not expected_path.exists()

        client.download(111)

        assert expected_path.exists()
        assert expected_path.read_bytes() == b"image data"

    def test_directory_path(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client)

        path = tmp_path
        expected_path = tmp_path / "image.jpg"

        assert not expected_path.exists()

        client.download(111, path)

        assert expected_path.exists()
        assert expected_path.read_bytes() == b"image data"

    @pytest.mark.parametrize(
        "fix_suffix, expected_file_name", [(True, "image.jpg"), (False, "image.png")]
    )
    def test_modify_suffix(
        self,
        tmp_path,
        requests_mock,
        make_client,
        setup,
        fix_suffix,
        expected_file_name,
    ):
        client = make_client()
        setup(client)

        path = tmp_path / "image.png"
        expected_path = tmp_path / expected_file_name

        assert not expected_path.exists()

        client.download(111, path, fix_suffix=fix_suffix)

        assert expected_path.exists()
        assert expected_path.read_bytes() == b"image data"

    def test_no_url(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client, url=None)

        path = tmp_path / "image.jpg"

        assert not path.exists()

        with pytest.raises(ClientException):
            client.download(111, path)

    def test_stream_false(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client)

        path = tmp_path / "image.jpg"

        assert not path.exists()

        client.download(111, path, stream=False)

        assert path.exists()
        assert path.read_bytes() == b"image data"

    def test_exists_file(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client)

        path = tmp_path / "image.jpg"
        path.touch()

        assert path.exists()

        with pytest.raises(FileExistsError):
            client.download(111, path)

    def test_exist_ok(self, tmp_path, requests_mock, make_client, setup):
        client = make_client()
        setup(client)

        path = tmp_path / "image.jpg"
        path.touch()

        assert path.exists()

        client.download(111, path, exist_ok=True)

        assert path.exists()
        assert path.read_bytes() == b"image data"

    @pytest.fixture
    def setup(self, requests_mock):
        def _setup(client, drawing_id=111, url="http://download.example.com/image.jpg"):
            requests_mock.get(
                f"{client._api_url}drawings/{drawing_id}/",
                json={"execStatus": "SUCCESS", "drawingUrl": url},
            )
            if url:
                requests_mock.get(url, content=b"image data")

        return _setup


class TestDownloadAndRead(object):
    def test_read_image(self, mocker, tmp_path, requests_mock, make_client, setup):
        expected = np.array([1])
        read_mock = mocker.MagicMock(return_value=expected)
        mocker.patch("anymotion_sdk.extras.read_image", read_mock)

        client = make_client()
        setup(client)

        image = client.download_and_read(111)

        assert image == expected

    def test_read_video(self, mocker, tmp_path, requests_mock, make_client, setup):
        expected = np.array([1])
        read_mock = mocker.MagicMock(return_value=expected)
        mocker.patch("anymotion_sdk.extras.read_video", read_mock)

        client = make_client()
        setup(client, url="http://download.example.com/movie.mp4")

        movie = client.download_and_read(111)

        assert movie == expected

    @pytest.fixture
    def setup(self, requests_mock):
        def _setup(client, drawing_id=111, url="http://download.example.com/image.jpg"):
            requests_mock.get(
                f"{client._api_url}drawings/{drawing_id}/",
                json={"execStatus": "SUCCESS", "drawingUrl": url},
            )
            if url:
                requests_mock.get(url, content=b"image data")

        return _setup


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
        assert requests_mock.call_count == len(response_list)

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
        assert requests_mock.call_count == 1

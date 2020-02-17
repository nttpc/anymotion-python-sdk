import pytest
import requests

from encore_sdk import RequestsError
from encore_sdk.session import HttpSession


class TestSession(object):
    @pytest.mark.parametrize("token", [None, "token"])
    def test_request(self, requests_mock, token):
        url = "http://example.com/"
        data = {"message": "success"}

        requests_mock.get(url, json=data)

        session = HttpSession()
        response = session.request(url, token=token)

        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert response.json() == data
        assert requests_mock.call_count == 1

    def test_request_post(self, requests_mock):
        url = "http://example.com/"
        data = {"message": "success"}

        requests_mock.post(url, json=data)

        session = HttpSession()
        response = session.request(url, "POST", json={"name": "image"})

        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert response.json() == data
        assert requests_mock.call_count == 1

    def test_add_request_callback(self, capfd, requests_mock):
        url = "http://example.com/"
        data = {"message": "success"}

        requests_mock.get(url, json=data)

        def f(r):
            print(r)

        session = HttpSession()
        session.add_request_callback(f)
        response = session.request(url)

        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert response.json() == data
        assert requests_mock.call_count == 1

        out, err = capfd.readouterr()
        assert out == "<Request [GET]>\n"
        assert err == ""

    def test_add_response_callback(self, capfd, requests_mock):
        url = "http://example.com/"
        data = {"message": "success"}

        requests_mock.get(url, json=data)

        def f(r):
            print(r)

        session = HttpSession()
        session.add_response_callback(f)
        response = session.request(url)

        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert response.json() == data
        assert requests_mock.call_count == 1

        out, err = capfd.readouterr()
        assert out == "<Response [200]>\n"
        assert err == ""

    def test_invalid_method(self, requests_mock):
        url = "http://example.com/"

        session = HttpSession()
        with pytest.raises(RequestsError) as excinfo:
            session.request(url, "INVALID")

        assert str(excinfo.value) == "HTTP method is invalid."

    def test_invalid_code(self, requests_mock):
        url = "http://example.com/"
        data = {"message": "error"}

        requests_mock.get(url, json=data, status_code=404)

        session = HttpSession()
        with pytest.raises(RequestsError) as excinfo:
            session.request(url)

        assert f"GET {url} is failed." in str(excinfo.value)

    def test_request_error(self, requests_mock):
        url = "http://example.com/"

        requests_mock.register_uri("GET", url, exc=requests.ConnectionError)

        session = HttpSession()
        with pytest.raises(RequestsError) as excinfo:
            session.request(url)

        assert str(excinfo.value) == f"GET {url} is failed."

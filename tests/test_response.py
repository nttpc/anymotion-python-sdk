import pytest

from encore_sdk import ResponseError
from encore_sdk.response import Response


class TestResponse(object):
    def test_read_json_property(self, mocker):
        response = Response(self._response_mock(mocker, {"id": 1}))

        assert response.json == {"id": 1}

    def test_read_status_property(self, mocker):
        response = Response(self._response_mock(mocker, {"execStatus": "SUCCESS"}))

        assert response.status == "SUCCESS"

    def test_set_status_property(self, mocker):
        response = Response(self._response_mock(mocker, {"execStatus": "PROCESSING"}))
        response.status = "TIMEOUT"

        assert response.status == "TIMEOUT"

    @pytest.mark.parametrize(
        "status, expected", [("SUCCESS", None), ("FAILURE", "message")]
    )
    def test_read_failure_detail_property(self, mocker, status, expected):
        response = Response(
            self._response_mock(
                mocker, {"execStatus": status, "failureDetail": "message"}
            )
        )

        assert response.failure_detail == expected

    @pytest.mark.parametrize("keys", ["value", ("value",)])
    def test_get(self, mocker, keys):
        response = Response(self._response_mock(mocker, {"value": 1}))
        (value,) = response.get(keys)

        assert value == 1

    def test_error_occurs_when_trying_to_get(self, mocker):
        response = Response(self._response_mock(mocker, {"value": 1}))
        with pytest.raises(ResponseError):
            response.get("non-existent")

    def _response_mock(self, mocker, return_value):
        ResponseMock = mocker.MagicMock()
        ResponseMock.return_value.json.return_value = return_value
        return ResponseMock()

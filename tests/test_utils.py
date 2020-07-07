import pytest

from anymotion_sdk.exceptions import ClientException
from anymotion_sdk.utils import check_endpoint


class TestCheckEndpoint(object):
    def test_available_endpoint(self):
        self.f("images")

    def test_unavailable_endpoint(self):
        with pytest.raises(ClientException) as excinfo:
            self.f("image")

        assert str(excinfo.value) == "Unavailable endpoints: image"

    @check_endpoint
    def f(self, endpoint):
        pass

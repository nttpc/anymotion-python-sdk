import pytest

from anymotion_sdk.auth import Authentication


@pytest.fixture
def make_auth(requests_mock):
    def _make_auth(tokens=["token"], issued_ats=["1580000000000"]):
        auth = Authentication("client_id", "client_secret")
        requests_mock.register_uri(
            "POST",
            "https://api.customer.jp/v1/oauth/accesstokens",
            [
                {
                    "json": {
                        "accessToken": token,
                        "issuedAt": issued_at,
                        "expiresIn": "86399",
                    }
                }
                for token, issued_at in zip(tokens, issued_ats)
            ],
        )
        return auth

    return _make_auth


class TestAuthentication(object):
    def test_token_is_none(self, make_auth):
        expected = "token"
        auth = make_auth(tokens=[expected])

        assert auth.token == expected

    def test_have_valid_token(self, mocker, make_auth):
        # NOTE: UNIX time 1700000000000 is 2023/11/14.
        auth = make_auth(
            tokens=["token1", "token2"], issued_ats=["1700000000000", "1700000000000"]
        )

        assert auth.token == "token1"
        assert auth.token == "token1"

    def test_token_expired(self, mocker, make_auth):
        auth = make_auth(
            tokens=["token1", "token2"], issued_ats=["1500000000000", "1500000000000"]
        )

        assert auth.token == "token1"
        assert auth.token == "token2"

from datetime import datetime
from logging import getLogger
from typing import Optional
from urllib.parse import urljoin

from .exceptions import ClientException, ClientValueError
from .session import HttpSession

logger = getLogger(__name__)


class Authentication(object):
    """Authenticate to AnyMotion."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.customer.jp/",
        session: Optional[HttpSession] = None,
    ):
        if client_id is None or client_id == "":
            raise ClientValueError("Client ID is not set.")

        if client_secret is None or client_secret == "":
            raise ClientValueError("Client Secret is not set.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.session = session or HttpSession()

        self._token = None

    @property
    def token(self) -> str:
        """Return access token."""
        if self._token is None:
            self._get_token()
            logger.info("Got your token.")
        elif self._is_expired():
            self._get_token()
            logger.info("Refreshed your token as it has expired.")

        if self._token is None:
            raise ClientException("The token could not get.")
        return self._token

    def _get_token(self) -> None:
        """Get a token using client ID and secret."""
        oauth_url = urljoin(self.base_url, "v1/oauth/accesstokens")
        data = {
            "grantType": "client_credentials",
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }
        response = self.session.request(oauth_url, method="POST", json=data)

        self._token = response.get("accessToken")

        issued_at = int(response.get("issuedAt")) / 10 ** 3
        expires_in = int(response.get("expiresIn"))
        self.expired_at = issued_at + expires_in

    def _is_expired(self, buffer: int = 300) -> bool:
        """Return whether or not the token has expired."""
        expired = datetime.fromtimestamp(self.expired_at - buffer)
        now = datetime.now()
        return expired < now

from typing import Optional
from urllib.parse import urljoin

from .session import HttpSession


def get_token(
    client_id: str,
    client_secret: str,
    base_url: str = "https://api.customer.jp/",
    session: Optional[HttpSession] = None,
) -> str:
    """Get a token using client ID and secret."""
    oauth_url = urljoin(base_url, "v1/oauth/accesstokens")
    session = session or HttpSession()
    data = {
        "grantType": "client_credentials",
        "clientId": client_id,
        "clientSecret": client_secret,
    }
    response = session.request(oauth_url, method="POST", json=data)
    return response.get("accessToken")

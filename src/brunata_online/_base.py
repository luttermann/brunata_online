from typing import Optional

import requests
from .auth import TokenManager


class BaseDataInterface:

    """
    Base class for fetching data from Brunata API.
    """
    def __init__(self, token: TokenManager):
        """
        :param token: TokenManager instance.
        """
        self.token = token
        self.s = requests.Session()
        self.s.headers.update(
            {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*',
            }
        )

    def _get(self, url: str, params: Optional[dict[str, str]] = None) -> dict | list:
        """
        Method to get JSON data from Brunata API.
        :param url: URL to fetch data from.
        :param params: dict of URL parameters.
        :return: JSON data in dict|list format.
        """
        token_headers = self.token.get_auth_header()
        self.s.headers.update(token_headers)
        resp = self.s.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

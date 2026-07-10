import base64
import json
from datetime import datetime
from typing import Optional

import requests

from ._types import JsonDict
from .auth import TokenManager, TokenData


class BrunataOnlineClient:
    def __init__(self, token: TokenData) -> None:
        self.token = token
        self.s = requests.Session()

    def _headers(self) -> dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def get(self, url: str, params: Optional[dict[str, str]] = None) -> JsonDict:
        self._update_token_headers()
        resp = self.s.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _update_token_headers(self) -> None:
        if self.token.expires_at is not None and self.token.expires_at + 60 < datetime.now():
            self.s.headers.update({
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            })
            return
        self._update_token()

    def _update_token(self) -> None:
        """Internal method to create use the refresh_token to get a renewed access."""

        # Start by format the Payload from the refresh_token
        token_parts = self.token.refresh_token.split('.')
        refresh_properties = token_parts[1]
        refresh_properties = refresh_properties + ('=' * (len(refresh_properties) % 4))
        refresh_properties = base64.b64decode(refresh_properties).decode('utf-8')
        refresh_properties = json.loads(refresh_properties)

        payload = {
            'client_id': refresh_properties['azp'],
            'refresh_token': self._token_data.refresh_token,
            'grant_type': 'refresh_token',
        }

        self.s.headers.clear()
        self.s.headers.update(self._headers())
        resp = self.s.post("token_refresh_endpoint", data=payload)
        self.token = TokenManager(resp.json())


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

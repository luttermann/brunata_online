import base64
import json
import time
from typing import Optional

import requests

from ._types import JsonDict
from .auth import TokenData


class BrunataOnlineClient:
    def __init__(self, token: TokenData) -> None:
        self.token = token
        self.s = requests.Session()

    def get(self, url: str, params: Optional[dict[str, str]] = None) -> JsonDict:
        self._update_token_headers()
        resp = self.s.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _update_token_headers(self) -> None:
        if self.token.expires_at is not None and self.token.expires_at + 60 > time.time():
            self.s.headers.update({
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            })
            from pprint import pp
            pp(self.s.headers)
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
            'refresh_token': self.token.refresh_token,
            'grant_type': 'refresh_token',
        }

        self.s.headers.clear()
        self.s.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        })
        resp = self.s.post('https://online.brunata.com/online-auth-webservice/v1/rest/oauth/token', data=payload)

        self.token = TokenData(**resp.json())

        self.s.headers.clear()
        self.s.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        })


class BaseDataInterface:
    def __init__(self, client: BrunataOnlineClient) -> None:
        self.client = client

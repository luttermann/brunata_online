import base64
import dataclasses
import json
from typing import Optional, Any
import time

import requests

from .types import JsonDict


@dataclasses.dataclass
class TokenData:
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    token_type: str
    id_token: str
    scope: str
    not_before_policy: int
    session_state: str
    expires_at: Optional[int] = None

    def __init__(self, **kwargs: Any):
        for arg_key, arg_value in kwargs.items():
            if arg_key == "not-before-policy":
                self.not_before_policy = arg_value
                continue
            setattr(self, arg_key, arg_value)
        if self.expires_at is None:
            self.expires_at = int(time.time()) + self.expires_in

    def asdict(self) -> JsonDict:
        data = dataclasses.asdict(self)
        data['not-before-policy'] = self.not_before_policy
        del data['not_before_policy']
        return data


class BrunataOnlineClient:
    """
    Client used for refreshing tokens, and requesting data from API endpoints.
    """
    def __init__(self, token: TokenData) -> None:
        self.token = token
        self.s = requests.Session()

    def get(self, url: str, params: Optional[dict[str, str]] = None) -> JsonDict:
        """Common method to get JSON data from URL endpoint. Ensuring that token is up to date.

        :param url: API endpoint url
        :type url: str
        :param params: http query parameters
        :type params: Optional[dict[str, str]]
        :return: JSON data from API endpoint
        :rtype: JsonDict
        """
        self._update_token_headers()
        resp = self.s.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _update_token_headers(self) -> None:
        """Internal: Set the Authorization header according to current TokenData, and update TokenData if needed"""
        if self.token.expires_at is not None and self.token.expires_at + 60 > time.time():
            self.s.headers.update({
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            })
            return
        self._update_token()
        if self.token.expires_at is not None and self.token.expires_at + 60 > time.time():
            self.s.headers.update({
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            })
        else:
            raise Exception('Unable to refresh token')

    def _update_token(self) -> None:
        """Internal method to use the refresh_token to get a renewed access."""

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

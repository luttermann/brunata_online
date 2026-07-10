import json
import pathlib
import base64
from typing import Optional, Any
import requests
import time

from ._types import JsonDict


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
    expires_at: Optional[int]

    def __init__(self, **kwargs):
        for arg_key, arg_value in kwargs.items():
            if arg_key == "not-before-policy":
                self.not_before_policy = arg_value
            else:
                setattr(self, arg_key, arg_value)

    def asdict(self) -> JsonDict:
        data = dataclasses.asdict(self)
        data['not-before-policy'] = self.not_before_policy
        del data['not_before_policy']
        return data



class LegacyTokenData:
    """
    Class for holding Token data.
    """
    def __init__(self) -> None:
        self._data: dict[str, str | int] = {}

    @staticmethod
    def from_dict(data: dict[str, int | str]) -> 'LegacyTokenData':
        """
        Create object from dict.
        :param data: dict containing the Token data as retuned from the authentication token endpoint.
        :return:
        """
        d = LegacyTokenData()
        if 'expires_at' not in data:
            data['expires_at'] = int(data.get('expires_in', 0)) + int(time.time())
        d._data = data
        return d

    def to_dict(self) -> dict:
        """
        Convert object to dict.
        :return: dict containing Token data.
        """
        return self._data

    @property
    def expires_at(self) -> Optional[int]:
        """
        Expiration time in Unix epoch format.
        :return: Returns None if time is not known or not yet calculated, else Unix epoch int.
        """
        try:
            value = self._data.get('expires_at', None)
            assert isinstance(value, int)
        except AssertionError:
            return None
        return value

    @expires_at.setter
    def expires_at(self, value: int) -> None:
        """
        Set the expiration time in Unix epoch format.
        :param value: int Unix epoch.
        :return: None
        """
        self._data['expires_at'] = value

    @property
    def refresh_token(self) -> str:
        """
        Refresh token
        :return: str The token to refresh the access token.
        """
        data = self._data.get('refresh_token', None)
        try:
            assert isinstance(data, str)
        except AssertionError as E:
            raise E
        return data

    @property
    def access_token(self) -> str:
        """
        Access token
        :return: str The token to use when using the API in general.
        """
        return str(self._data.get('access_token'))


def as_token_data(data: dict) -> LegacyTokenData:
    """
    Helper function to cast json data directly into a LegacyTokenData object.
    :param data: decoded JSON data.
    :return: LegacyTokenData object.
    """
    return LegacyTokenData.from_dict(data)


class JsonTokenData(json.JSONEncoder):
    """
    Helper class to cast LegacyTokenData object into json.
    """
    def default(self, obj: object) -> dict:
        if isinstance(obj, LegacyTokenData):
            return obj.to_dict()
        return super().default(obj)


class TokenManager:
    def __init__(self, storage_file: pathlib.Path):
        """
        TokenManager class to update load and store the token data.

        :param storage_file: Path to storage token file
        """
        self._token_data: LegacyTokenData
        self.storage_file = storage_file
        self._load()

    def _load(self) -> None:
        """Internal load method, to load token data from storage file."""
        with self.storage_file.open('rt') as fp:
            self._token_data = json.load(fp, object_hook=as_token_data)
            if self._token_data.expires_at is None:
                self.refresh_token()

    def _save(self) -> None:
        """Internal save method, to save token data to storage file."""
        if self._token_data.access_token is not None or self._token_data.refresh_token is not None:
            with self.storage_file.open('w') as fp:
                json.dump(self._token_data, fp, cls=JsonTokenData, indent=4)

    def _create_refresh_payload(self) -> dict[str, str]:
        """Internal method to create payload for refreshing tokens."""
        token_parts = self._token_data.refresh_token.split('.')
        refresh_properties = token_parts[1]
        refresh_properties = refresh_properties + ('=' * (len(refresh_properties) % 4))
        refresh_properties = base64.b64decode(refresh_properties).decode('utf-8')
        refresh_properties = json.loads(refresh_properties)

        return {
            'client_id': refresh_properties['azp'],
            'refresh_token': self._token_data.refresh_token,
            'grant_type': 'refresh_token',
        }

    def refresh_token(self) -> None:
        """Refresh the access token.
        Raises requests.exceptions.HTTPError on Error
        :return: None
        """
        resp = requests.post(
            'https://online.brunata.com/online-auth-webservice/v1/rest/oauth/token',
            data=self._create_refresh_payload(),
        )

        resp.raise_for_status()
        self._token_data = LegacyTokenData.from_dict(resp.json())

    def get_auth_header(self) -> dict[str, str]:
        """Create a dict containing Authorization headers for API usage"""
        self.refresh_token()
        if self._token_data.expires_at is None:
            raise Exception('TokenManager has not been initialized')
        if time.time() + 60 > self._token_data.expires_at:
            self.refresh_token()

        return {
            'Authorization': 'Bearer ' + str(self._token_data.access_token)
        }

    def dump_token(self) -> dict[str, str]:
        """Dump the token data, primarily usable for debugging."""
        return self._token_data.to_dict()

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self._save()

    def __enter__(self) -> "TokenManager":
        return self

    def __del__(self) -> None:
        self._save()

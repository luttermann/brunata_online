"""
Brunata user access
"""
from ._base import BaseDataInterface
from typing import Any


class BrunataUser(BaseDataInterface):
    def get_user(self) -> dict[str, Any]:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/user')
        return data

    def get_consumer(self) -> dict[str, Any]:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer')
        return data

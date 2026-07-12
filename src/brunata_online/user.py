"""
Brunata user access
"""
from .base import BaseDataInterface
from .types import JsonDict


class BrunataUser(BaseDataInterface):
    def get_user(self) -> JsonDict:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/user')
        return data

    def get_consumer(self) -> JsonDict:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer')
        return data

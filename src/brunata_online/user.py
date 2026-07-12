"""
Brunata user access
"""
from ._base import BaseDataInterface
from ._types import JsonDict


class BrunataUser(BaseDataInterface):
    def get_user(self) -> JsonDict:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/user')
        return data

    def get_consumer(self) -> JsonDict:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer')
        return data

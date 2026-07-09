"""
Brunata user access
"""
from ._base import BaseDataInterface
from typing import Any


class BrunataUser(BaseDataInterface):
    def get_user(self) -> dict[Any, Any] | list[Any]:
        """Get information about the Brunata user (User account)"""
        data = self._get('https://online.brunata.com/online-webservice/v2/rest/user')
        return data

    def get_consumer(self) -> dict[Any, Any] | list[Any]:
        """Get information about the consumer (Information aboutn the consumer where meters are installed)"""
        data = self._get('https://online.brunata.com/online-webservice/v2/rest/consumer')
        return data

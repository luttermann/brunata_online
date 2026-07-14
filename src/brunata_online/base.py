import abc
from .auth import BrunataOnlineClient


class BaseDataInterface(abc.ABC):
    """
    Base class for all data interfaces.

    Data interface must be initialized with a BrunataOnlineClient instance.

    :param client: Client for using the API
    :type client: BrunataOnlineClient
    """
    def __init__(self, client: BrunataOnlineClient) -> None:
        self.client = client

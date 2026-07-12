from .auth import BrunataOnlineClient


class BaseDataInterface:
    def __init__(self, client: BrunataOnlineClient) -> None:
        self.client = client

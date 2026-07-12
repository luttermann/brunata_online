import dataclasses
from typing import Optional, Any
import time
from ._types import JsonDict


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

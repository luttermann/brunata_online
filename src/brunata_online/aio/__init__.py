import base64
import json
import time
import datetime
import aiohttp
from typing import Optional

from .. import TokenData, MeterOverview, MeterValues, ConsumptionData
from ..types import JsonDict, Interval


class BrunataHttpError(Exception):
    pass


class BrunataOnlineAsyncClient:
    def __init__(self, token: TokenData) -> None:
        self.token = token
        self._headers: dict[str, str] = {}

    async def get(self, url: str, params: Optional[dict[str, str]] = None) -> JsonDict:
        await self._update_token_headers()
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(url, params=params) as resp:
                if resp.status > 299:
                    raise BrunataHttpError(
                        f'Unable to get {url} with params: {str(params)}; status: ' + str(resp.status)
                    )
                return await resp.json()

    async def _update_token_headers(self) -> None:
        if self.token.expires_at is not None and self.token.expires_at + 60 > time.time():
            self._headers.update({
                "Authorization": f"{self.token.token_type} {self.token.access_token}",
            })
            return
        await self._update_token()

    async def _update_token(self) -> None:
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

        self._headers.clear()
        self._headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        })
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.post(
                    url='https://online.brunata.com/online-auth-webservice/v1/rest/oauth/token',
                    data=payload
            ) as resp:
                if resp.status > 299:
                    raise BrunataHttpError("Unable to update token")
                json_body = await resp.json()
                self.token = TokenData(**json_body)

        self._headers.clear()
        self._headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        })


class BaseDataAsyncInterface:
    def __init__(self, client: BrunataOnlineAsyncClient) -> None:
        self.client = client


class BrunataAsyncUser(BaseDataAsyncInterface):
    async def get_user(self) -> JsonDict:
        data = await self.client.get('https://online.brunata.com/online-webservice/v2/rest/user')
        return data

    async def get_consumer(self) -> JsonDict:
        data = await self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer')
        return data


class MeterAsyncApi(BaseDataAsyncInterface):
    async def meteroverview(self) -> list[MeterOverview]:
        data = await self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer/meteroverview')
        meters: list[MeterOverview] = []
        for meter in data:
            assert isinstance(meter, dict)
            meters.append(MeterOverview(**meter))
        return meters

    async def consumption(self,
                          startdate: datetime.datetime,
                          enddate: datetime.datetime,
                          interval: Interval,
                          allocationunit: str = "K") -> ConsumptionData:
        if startdate.tzinfo is None or enddate.tzinfo is None:
            raise Exception('startdate and enddate must have timezone info')

        # startdate = startdate.replace(minute=0, second=0, microsecond=0)
        # enddate = enddate.replace(minute=0, second=0, microsecond=0)

        params = {
            "startdate": startdate.isoformat(),
            "enddate": enddate.isoformat(),
            "interval": interval.value,
            "allocationunit": allocationunit,
        }

        data = await self.client.get(
            url='https://online.brunata.com/online-webservice/v2/rest/consumer/consumption',
            params=params
        )
        return ConsumptionData(**data)

    async def metervalues(self,
                          start_date: datetime.datetime,
                          end_date: datetime.datetime,
                          meter: int) -> MeterValues:

        if start_date.tzinfo is None or end_date.tzinfo is None:
            raise Exception('start_date and end_date must have timezone info')

        params = {
            "startdate": start_date.isoformat(timespec='milliseconds'),
            "enddate": end_date.isoformat(timespec='milliseconds'),
        }

        data = await self.client.get("https://online.brunata.com/online-webservice/v2/rest/consumer/meters/" +
                                     str(meter) + "/metervalues",
                                     params=params
                                     )
        return MeterValues(**data)

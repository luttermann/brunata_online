import json
import asyncio
import pytz
import datetime

from brunata_online import TokenData, Interval
from brunata_online.aio import BrunataAsyncUser, BrunataOnlineAsyncClient, MeterAsyncApi


async def main(token: TokenData) -> None:
    time_zone = pytz.timezone('Europe/Copenhagen')

    client = BrunataOnlineAsyncClient(token)
    user = BrunataAsyncUser(client)
    meter = MeterAsyncApi(client)

    print("USER:")
    print(await user.get_user())
    print("CONSUMER:")
    print(await user.get_consumer())
    print("METER:")
    meter_overview = await meter.meteroverview()
    print(meter_overview)

    print("METER VALUES:")
    meter_values = await meter.metervalues(
        meter=meter_overview[0].meterId,
        start_date=datetime.datetime.now(tz=time_zone) - datetime.timedelta(days=1),
        end_date=datetime.datetime.now(tz=time_zone),
    )
    print(meter_values)

    print("CONSUMPTION:")
    consumption_data = await meter.consumption(
        startdate=datetime.datetime.now(tz=time_zone) - datetime.timedelta(days=1),
        enddate=datetime.datetime.now(tz=time_zone),
        interval=Interval.HOUR,
    )
    print(consumption_data)

if __name__ == "__main__":
    with open('token', 'r') as fh:
        token_dict = json.load(fh)
    token = TokenData(**token_dict)
    asyncio.run(main(token))

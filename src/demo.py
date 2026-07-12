import datetime
from pprint import pp
import json
import pytz

from brunata_online import BrunataOnlineClient, TokenData, BrunataUser, MeterApi, Interval

# import logging
# import http.client
#
# http.client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

tz = pytz.timezone('Europe/Copenhagen')

with open('.token.json', 'r') as f:
    td = TokenData(**json.load(f))

client = BrunataOnlineClient(td)

us = BrunataUser(client)
us.get_user()
mt = MeterApi(client)
my_meters = mt.meteroverview()
assert len(my_meters) > 0

meter_values = mt.metervalues(
    meter=my_meters[0].meterId,
    start_date=datetime.datetime.now(tz=tz) - datetime.timedelta(days=2),
    end_date=datetime.datetime.now(tz=tz),
)

pp(meter_values)

cons = mt.consumption(
    startdate=datetime.datetime.now(tz=tz) - datetime.timedelta(days=2),
    enddate=datetime.datetime.now(tz=tz),
    interval=Interval.HOUR,
)

pp(cons)

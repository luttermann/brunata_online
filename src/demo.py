import datetime
from pprint import pp
import json
import pytz

from brunata_online import BrunataOnlineClient, TokenData, BrunataUser, MeterApi, Interval

# Create a TokenData object to use at authentication against the API (read it from a file)
token_fh = open('token', 'r+')
td = TokenData(**json.load(token_fh))

# Load the local timezone, for use with start_date/end_date when getting meter data.
time_zone = pytz.timezone('Europe/Copenhagen')

# Create a client with the token
client = BrunataOnlineClient(td)

# Create a BrunataUser object to handle getting user data
user = BrunataUser(client)
pp(user.get_user())

# Create a MeterApi to get information about the meters that you can access.
meters = MeterApi(client)
my_meters = meters.meteroverview()
pp(my_meters)

# Fetch information about the meter values (past 24 hours)
meter_values = meters.metervalues(
    meter=my_meters[0].meterId,
    start_date=datetime.datetime.now(tz=time_zone) - datetime.timedelta(days=1),
    end_date=datetime.datetime.now(tz=time_zone),
)

pp(meter_values)

# Fetch consumption for all meters for every `interval` (past 24 hours)
consumption = meters.consumption(
    start_date=datetime.datetime.now(tz=time_zone) - datetime.timedelta(days=1),
    end_date=datetime.datetime.now(tz=time_zone),
    interval=Interval.HOUR,
)

pp(consumption)

# Save the, possibly refreshed, token back into the initial token file.
token_fh.seek(0)
token_fh.truncate()
token_fh.write(json.dumps(td.asdict(), indent=4))
token_fh.close()

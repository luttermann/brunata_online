import pathlib
from brunata_online import BrunataUser, TokenManager
from brunata_online.usage import MeterInformation
from pprint import pp

tm = TokenManager(pathlib.Path(__file__).parent / '.token.json')

user = BrunataUser(tm)
meter = MeterInformation(tm)

print("###################### user.get_user() ######################")
pp(user.get_user())
print("###################### user.get_consumer() ######################")
pp(user.get_consumer())
print("###################### meter.meteroverview() ######################")
pp(meter.meteroverview())
print("###################### meter.meterforconsumer() ######################")
pp(meter.metersforconsumer())

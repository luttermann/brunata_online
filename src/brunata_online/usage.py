import dataclasses
from typing import Optional
import datetime
import enum
from ._base import BaseDataInterface


class Units(enum.IntEnum):
    SQUARE_METERS = 8


@dataclasses.dataclass
class ConsumptionMeterInformation:
    meterId: int
    placement: str
    meterNo: str
    meterType: int
    mountingDate: datetime.datetime  # "2026-01-28T00:00:00+01:00",
    transmitting: bool
    allocationUnit: str              # 'K'
    superAllocationUnit: int
    unit: Units                      # Cast from string "8"
    meterSequenceNo: int
    decimals: int
    dismountedDate: Optional[datetime.datetime] = None
    unitfactor: Optional[object] = None
    unitReduction: Optional[object] = None
    scale: Optional[object] = None
    numerator: Optional[object] = None
    denominator: Optional[object] = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == "mountingDate":
                setattr(self, key, datetime.datetime.fromisoformat(value))
                continue
            if key == "dismountedDate":
                try:
                    setattr(self, key, datetime.datetime.fromisoformat(value))
                except TypeError:
                    setattr(self, key, None)
                continue
            if key == "unit":
                setattr(self, key, Units(int(value)))
                continue
            setattr(self, key, value)


@dataclasses.dataclass
class MeterOverview:
    meterId: int
    consumptionLast30Days: float
    unit: Units
    alloUnitType: str
    meterValue: float
    telegramDate: datetime.datetime
    countingMethod: str
    isConsumption: bool
    placement: str
    meterNo: int
    decimals: int
    consumptionPriorYearSamePeriod: Optional[float] = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'unit':
                setattr(self, 'unit', Units(int(value)))
                continue
            setattr(self, key, value)


class Interval(enum.StrEnum):
    HOUR = 'H'
    DAY = 'D'
    MONTH = 'M'
    YEAR = 'Y'


@dataclasses.dataclass
class ConsumptionDataLineValue:
    fromDate: datetime.datetime
    toDate: datetime.datetime
    consumption: float


@dataclasses.dataclass
class ConsumptionDataLines:
    meter: ConsumptionMeterInformation
    consumptionValues: list[ConsumptionDataLineValue]


@dataclasses.dataclass
class ConsumptionData:
    startDate: datetime.datetime
    endDate: datetime.datetime
    interval: Interval
    consumptionLines: list[ConsumptionDataLines]

    def __init__(self, **kwargs):
        start_date = kwargs.pop('startDate')
        self.startDate = datetime.datetime.fromisoformat(start_date)
        end_date = kwargs.pop('endDate')
        self.endDate = datetime.datetime.fromisoformat(end_date)
        interval = kwargs.pop('interval')
        self.interval = Interval(interval)
        consumption_lines_data = kwargs.pop('consumptionLines')
        self.consumptionLines = self._create_consumption_lines(consumption_lines_data)

    @staticmethod
    def _create_consumption_lines(values: list[dict]) -> list[ConsumptionDataLines]:
        lines = []
        for val in values:
            from pprint import pprint
            pprint(val['meter'])
            meter = ConsumptionMeterInformation(**val['meter'])
            data_line = ConsumptionDataLines(meter=meter, consumptionValues=[])
            for cv in val['consumptionValues']:
                data_line.consumptionValues.append(ConsumptionDataLineValue(**cv))
            lines.append(data_line)
        return lines


@dataclasses.dataclass
class MeterValue:
    readingDate: datetime.datetime
    value: float
    unit: Units

    def __init__(self, **kwargs):
        self.readingDate = datetime.datetime.fromisoformat(kwargs['readingDate'])
        self.value = kwargs['value']
        self.unit = Units(kwargs['unit'])


@dataclasses.dataclass
class MeterValues:
    meterValues: list[MeterValue]
    limited: bool
    yAxisStart: int
    yAxisEnd: int

    def __init__(self, **kwargs):
        self.limited = kwargs['limited']
        self.yAxisStart = kwargs['yAxisStart']
        self.yAxisEnd = kwargs['yAxisEnd']
        self.meterValues = MeterValues._meter_value_list(kwargs['meterValues'])

    @staticmethod
    def _meter_value_list(meter_values: list[dict[str, object]]):
        values_list = []
        for value in meter_values:
            values_list.append(MeterValue(**value))
        return values_list


class Meters(BaseDataInterface):
    def meteroverview(self) -> list[MeterOverview]:
        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer/meteroverview')
        meters: list[MeterOverview] = []
        for meter in data:
            assert isinstance(meter, dict)
            meters.append(MeterOverview(**meter))
        return meters

    def consumption(self, startdate: datetime.datetime, enddate: datetime.datetime, interval: Interval,
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

        data = self.client.get('https://online.brunata.com/online-webservice/v2/rest/consumer/consumption',
                               params=params)
        return ConsumptionData(**data)

    def metervalues(self,
                    start_date: datetime.datetime,
                    end_date: datetime.datetime,
                    meter: int) -> MeterValues:

        if start_date.tzinfo is None or end_date.tzinfo is None:
            raise Exception('start_date and end_date must have timezone info')

        params = {
            "startdate": start_date.isoformat(timespec='milliseconds'),
            "enddate": end_date.isoformat(timespec='milliseconds'),
        }

        data = self.client.get("https://online.brunata.com/online-webservice/v2/rest/consumer/meters/" +
                               str(meter) + "/metervalues",
                               params=params
                               )
        return MeterValues(**data)

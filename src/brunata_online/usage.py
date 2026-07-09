from typing import Any
import datetime
import enum
from ._base import BaseDataInterface


class Units(enum.IntEnum):
    SQUARE_METERS = 8


class MeterInformation(BaseDataInterface):
    def meteroverview(self) -> dict[Any, Any] | list[Any]:
        """Returns a list of active meters available

        Example of returned json data::

        .. code-block:: json

          [
          {'meterId': 1234567890,
          'consumptionLast30Days': 1.234,
          'consumptionPriorYearSamePeriod': None,
          'unit': 8,
          'alloUnitType': 'K',
          'meterValue': 123.123,
          'telegramDate': '2026-07-06T21:00:00+02:00',
          'countingMethod': 'T',
          'isConsumption': True,
          'placement': 'Main valve',
          'meterNo': '0123456789012345',
          'decimals': 3}]

        :return:
        """
        data = self._get('https://online.brunata.com/online-webservice/v2/rest/consumer/meteroverview')
        return data

    def metersforconsumer(self) -> dict[Any, Any] | list[Any]:
        """List all meters, even meters that have been decommissioned."""
        data = self._get('https://online.brunata.com/online-webservice/v2/rest/consumer/metersforconsumer')
        return data


class MeterReadings(BaseDataInterface):
    """Reading meter values and consumption"""
    def metervalues(self, startdate: datetime.datetime, enddate: datetime.datetime, meter: int) -> dict:
        """
        TODO: Expand this section
        :param startdate:
        :param enddate:
        :param meter:
        :return:
        """
        if startdate.tzinfo is None or enddate.tzinfo is None:
            raise Exception('startdate and enddate must have timezone info')

        params = {
            "startdate": startdate.isoformat(timespec='milliseconds'),
            "enddate": enddate.isoformat(timespec='milliseconds'),
        }

        data = self._get("https://online.brunata.com/online-webservice/v2/rest/consumer/meters/" +
                         str(meter) + "/metervalues",
                         params=params
                         )
        assert isinstance(data, dict)
        return data

    def consumption(self,
                    startdate: datetime.datetime,
                    enddate: datetime.datetime,
                    interval: str,
                    allocation: str = "K") -> dict:
        """
        TODO: Expand this section
        Returns consumption data
        :param startdate: ISO8601 format datetime, eks: YYYY-MM-DDTHH:MM:SS.fff+HH:MM
        :param enddate: ISO8601 format datetime, eks: YYYY-MM-DDTHH:MM:SS.fff+HH:MM
        :param interval: 'H': Hour, 'D': Day, 'M': Month,'Y': Year
        :param allocation: I don't actually know what this is, but it is always 'K'
        :return:
           {
             "startDate" : "2026-06-02T00:00:00+02:00",
             "endDate" : "2026-07-02T00:00:00+02:00",
             "interval" : "D",
             "consumptionLines" : [ {
               "meter" : {
                 "meterId" : 18031105,
                 "placement" : "Bryggers",
                 "meterNo" : "04B6489961240358",
                 "meterType" : 2,
                 "scale" : null,
                 "unitfactor" : null,
                 "unitReduction" : null,
                 "mountingDate" : "2026-01-28T00:00:00+01:00",
                 "dismountedDate" : null,
                 "transmitting" : true,
                 "allocationUnit" : "K",
                 "superAllocationUnit" : 2,
                 "unit" : "8",
                 "meterSequenceNo" : 21,
                 "numerator" : null,
                 "denominator" : null,
                 "decimals" : 3
               },
               "consumptionValues" : [ {
                 "fromDate" : "2026-06-02T00:00:00+02:00",
                 "toDate" : "2026-06-03T00:00:00+02:00",
                 "consumption" : 0.169
               }, {
                 "fromDate" : "2026-06-03T00:00:00+02:00",
                 "toDate" : "2026-06-04T00:00:00+02:00",
                 "consumption" : 0.173
               }, {
                 "fromDate" : "2026-06-04T00:00:00+02:00",
                 "toDate" : "2026-06-05T00:00:00+02:00",
                 "consumption" : 0.070
               }, {
        """
        if startdate.tzinfo is None or enddate.tzinfo is None:
            raise Exception('startdate and enddate must have timezone info')

        params = {
            "startdate": startdate.isoformat(timespec='milliseconds'),
            "enddate": enddate.isoformat(timespec='milliseconds'),
            "interval": interval,
            "allocation": allocation,
        }

        data = self._get('https://online.brunata.com/online-webservice/v2/rest/consumer/consumption',
                         params=params)
        assert isinstance(data, dict)
        return data

"""
COVID-19 Reported Patient Impact and Hospital Capacity by State Timeseries

https://dev.socrata.com/foundry/healthdata.gov/g62h-syeh
https://github.com/xmunoz/sodapy
"""
from sodapy import Socrata
from datetime import date, datetime
from functools import cached_property
from config.secrets import SODA_APP_TOKEN


EXTRACT_URL = 'sandbox.demo.socrata.com'
DATASET_ID = 'g62h-syeh'
START_DATE = date(2020, 3, 1)


class HHSDailyPatientsExtract:
    #
    # Properties
    #
    @cached_property
    def hospitalizations(self):
        col_name = 'total_adult_patients_hospitalized_confirmed_and_suspected_covid'
        return self.daily_totals(col_name)

    @cached_property
    def icu_cases(self):
        col_name = 'staffed_icu_adult_patients_confirmed_and_suspected_covid'
        return self.daily_totals(col_name)

    @property
    def dates(self):
        return sorted(self.daily_logs.keys())

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    #
    # Private
    #
    @cached_property
    def cdc_data(self):
        start_date_iso = datetime.combine(START_DATE, datetime.min.time()).isoformat()
        parameters = {
            '$where': "date >= '{}'".format(start_date_iso),
        }

        client = Socrata(EXTRACT_URL, SODA_APP_TOKEN)
        return client.get_all(DATASET_ID, **parameters)

    @cached_property
    def daily_logs(self):
        daily_logs = {}

        for daily_state_data in self.cdc_data:
            dated = datetime.fromisoformat(daily_state_data['date']).date()

            if daily_logs.get(dated):
                daily_logs[dated].append(daily_state_data)
            else:
                daily_logs[dated] = [daily_state_data]

        return daily_logs

    def daily_totals(self, column):
        daily_totals = {}
        for dated in self.dates:
            daily_totals[dated] = self.daily_total(dated, column)
        return daily_totals

    def daily_total(self, dated, column):
        daily_national_total = 0

        for daily_log in self.daily_logs[dated]:
            value = daily_log.get(column, '0')
            state_total = int(float(value))
            daily_national_total += state_total

        return daily_national_total

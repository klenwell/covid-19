"""
United States COVID-19 Cases and Deaths by State over Time

https://dev.socrata.com/foundry/data.cdc.gov/9mfq-cb36
https://github.com/xmunoz/sodapy
"""
from sodapy import Socrata
from datetime import date, datetime
from functools import cached_property
from config.secrets import SODA_APP_TOKEN


EXTRACT_URL = 'data.cdc.gov'
DATASET_ID = '9mfq-cb36'
START_DATE = date(2020, 3, 1)


class CdcDailyCasesExtract:
    #
    # Properties
    #
    @cached_property
    def new_cases(self):
        col_name = 'new_case'
        return self.daily_totals(col_name)

    @cached_property
    def new_deaths(self):
        col_name = 'new_death'
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

    @cached_property
    def cdc_data(self):
        start_date_iso = datetime.combine(START_DATE, datetime.min.time()).isoformat()
        parameters = {
            '$where': "submission_date >= '{}'".format(start_date_iso),
        }

        client = Socrata(EXTRACT_URL, SODA_APP_TOKEN)
        return client.get_all(DATASET_ID, **parameters)

    @cached_property
    def daily_logs(self):
        daily_logs = {}

        for daily_state_data in self.cdc_data:
            dated = datetime.fromisoformat(daily_state_data['submission_date']).date()

            if daily_logs.get(dated):
                daily_logs[dated].append(daily_state_data)
            else:
                daily_logs[dated] = [daily_state_data]

        return daily_logs

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    #
    # Private
    #
    def daily_totals(self, column):
        daily_totals = {}
        for dated in self.dates:
            daily_totals[dated] = self.daily_total(dated, column)
        return daily_totals

    def daily_total(self, dated, column):
        daily_national_total = 0

        for daily_log in self.daily_logs[dated]:
            # On 2021-04-21, new_case column disappeared from MO's daily log
            reported_total = daily_log.get(column, '0.0')
            state_total = int(float(reported_total))
            daily_national_total += state_total

        return daily_national_total

"""
COVID-19 Diagnostic Laboratory Testing (PCR Testing) Time Series

https://dev.socrata.com/foundry/healthdata.gov/j8mb-icvb
https://github.com/xmunoz/sodapy
"""
from sodapy import Socrata
from datetime import date, datetime
from functools import cached_property
from config.secrets import SODA_APP_TOKEN


EXTRACT_URL = 'healthdata.gov'
DATASET_ID = 'j8mb-icvb'
START_DATE = date(2020, 3, 1)


class HHSDailyTestsExtract:
    #
    # Properties
    #
    @cached_property
    def new_tests(self):
        daily_totals = {}
        for dated in self.dates:
            positives = self.positive_tests.get(dated, 0)
            negatives = self.negative_tests.get(dated, 0)
            daily_totals[dated] = negatives + positives
        return daily_totals

    @cached_property
    def positive_tests(self):
        outcome_value = 'Positive'
        return self.daily_outcome_totals(outcome_value)

    @cached_property
    def negative_tests(self):
        outcome_value = 'Negative'
        return self.daily_outcome_totals(outcome_value)

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

    def daily_outcome_totals(self, outcome):
        daily_totals = {}
        for dated in self.dates:
            daily_totals[dated] = self.daily_outcome_total(dated, outcome)
        return daily_totals

    def daily_outcome_total(self, dated, outcome):
        daily_national_total = 0

        for daily_log in self.daily_logs[dated]:
            if daily_log['overall_outcome'].lower() != outcome.lower():
                continue

            state_total = int(float(daily_log['new_results_reported']))
            daily_national_total += state_total

        return daily_national_total

import requests
from datetime import datetime
from functools import cached_property


EXTRACT_URL = 'https://covidtracking.com/api/v1/us/daily.json'
DATE_F = '%Y%m%d'


class AtlanticCovidTrackingExtract:
    #
    # Static Methods
    #
    @staticmethod
    def us_daily_extract():
        """Returns instance of extract.
        """
        extract = AtlanticCovidTrackingExtract()
        extract.fetch_data_source()
        return extract

    #
    # Properties
    #
    @cached_property
    def data_dict(self):
        data_dict = {}
        for daily_data in self.json:
            date_str = str(daily_data['date'])
            reported_on = datetime.strptime(date_str, DATE_F).date()
            data_dict[reported_on] = daily_data
        return data_dict

    @cached_property
    def dates(self):
        return sorted(self.data_dict.keys())

    @cached_property
    def last_date(self):
        return self.dates[-1]

    @cached_property
    def new_tests(self):
        col_name = 'totalTestResultsIncrease'
        new_tests = {}
        for dated in self.dates:
            new_tests[dated] = self.daily_column(dated, col_name)
        return new_tests

    @cached_property
    def new_cases(self):
        col_name = 'positiveIncrease'
        new_cases = {}
        for dated in self.dates:
            new_cases[dated] = self.daily_column(dated, col_name)
        return new_cases

    @cached_property
    def new_deaths(self):
        col_name = 'deathIncrease'
        new_deaths = {}
        for dated in self.dates:
            new_deaths[dated] = self.daily_column(dated, col_name)
        return new_deaths

    @cached_property
    def hospitalizations(self):
        col_name = 'hospitalizedCurrently'
        hospitalizations = {}
        for dated in self.dates:
            hospitalizations[dated] = self.daily_column(dated, col_name)
        return hospitalizations

    @cached_property
    def icu_cases(self):
        col_name = 'inIcuCurrently'
        icu_cases = {}
        for dated in self.dates:
            icu_cases[dated] = self.daily_column(dated, col_name)
        return icu_cases

    #
    # Instance Methods
    #
    def __init__(self):
        self.url = EXTRACT_URL
        self.json = None

    def fetch_data_source(self):
        response = requests.get(self.url)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        self.json = response.json()
        return self.json

    #
    # Private
    #
    def daily_column(self, dated, column):
        data_on_date = self.data_dict.get(dated, {})
        return data_on_date.get(column)

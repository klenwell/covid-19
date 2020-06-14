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
    def daily_us_data():
        """Returns a dict: {date: {new-cases: n, ...}, ...} for US.
        """
        extract = AtlanticCovidTrackingExtract()
        html = extract.fetch_data_source()
        daily_dict = extract.filter_us_data(html)
        return daily_dict

    #
    # Properties
    #
    @cached_property
    def header_row(self):
        pass

    @cached_property
    def data_dict(self):
        pass

    @cached_property
    def dates(self):
        return sorted(self.data_dict.keys())

    @cached_property
    def new_cases(self):
        pass

    @cached_property
    def new_tests(self):
        pass

    @cached_property
    def hospitalizations(self):
        pass

    @cached_property
    def icu_cases(self):
        pass

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

    def filter_us_data(self, html):
        pass

    #
    # Private
    #

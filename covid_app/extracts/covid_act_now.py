from datetime import datetime
from urllib.parse import urljoin
import requests
from functools import cached_property


BASE_URL = 'https://data.covidactnow.org'
DATE_F = '%Y-%m-%d'


class CovidActNowExtract:
    #
    # Static Methods
    #
    @staticmethod
    def oc_effective_reproduction():
        """Returns extract with data for Orange County, CA.
        """
        url_path = '/snapshot/1290/v2/county/06059.timeseries.json'
        url = urljoin(BASE_URL, url_path)
        return CovidActNowExtract(url)

    @staticmethod
    def us_effective_reproduction():
        """Returns extract with data for US.
        """
        pass

    #
    # Properties
    #
    @cached_property
    def json_data(self):
        response = requests.get(self.url)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        return response.json()

    @cached_property
    def metrics_timeseries(self):
        timeseries = {}
        for daily_data in self.json_data['metricsTimeseries']:
            date_str = str(daily_data['date'])
            reported_on = datetime.strptime(date_str, DATE_F).date()
            timeseries[reported_on] = daily_data
        return timeseries

    @cached_property
    def actuals_timeseries(self):
        timeseries = {}
        for daily_data in self.json_data['actualsTimeseries']:
            date_str = str(daily_data['date'])
            reported_on = datetime.strptime(date_str, DATE_F).date()
            timeseries[reported_on] = daily_data
        return timeseries

    @cached_property
    def dates(self):
        return sorted(self.actuals_timeseries.keys())

    @cached_property
    def last_date(self):
        return self.dates[-1]

    #
    # Instance Methods
    #
    def __init__(self, url):
        self.url = url

    #
    # Private
    #

from datetime import datetime
from urllib.parse import urljoin
import requests
from functools import cached_property
from config.secrets import COVID_ACT_NOW_API_KEY as API_KEY


BASE_URL = 'https://api.covidactnow.org'
COUNTY_API_PATH = "/v2/county/{fips}.timeseries.json?apiKey={api_key}"
COUNTRY_API_PATH = "/v2/TBA.json?apiKey={api_key}"
DATE_F = '%Y-%m-%d'


class CovidActNowExtract:
    #
    # Static Methods
    #
    @staticmethod
    def oc_effective_reproduction():
        """Returns extract with data for Orange County, CA.
        """
        return CovidActNowExtract(fips="06059")

    @staticmethod
    def kent_effective_reproduction():
        """Returns extract with data for Kent County, MI.
        """
        return CovidActNowExtract(fips="26081")

    @staticmethod
    def us_effective_reproduction():
        """Returns extract with data for US.
        """
        return CovidActNowExtract()

    #
    # Properties
    #
    @property
    def api_url(self):
        if self.fips:
            url_path = COUNTY_API_PATH.format(fips=self.fips, api_key=API_KEY)
        else:
            url_path = COUNTRY_API_PATH.format(api_key=API_KEY)

        return urljoin(BASE_URL, url_path)

    @cached_property
    def json_data(self):
        print(self.api_url)
        response = requests.get(self.api_url)
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

    @property
    def dates(self):
        return sorted(self.actuals_timeseries.keys())

    @property
    def last_date(self):
        return self.dates[-1]

    @property
    def infection_rates(self):
        timeseries = {}
        for dated in self.dates:
            daily_data = self.metrics_timeseries.get(dated, {})
            timeseries[dated] = daily_data.get('infectionRate')
        return timeseries

    @property
    def hospital_beds(self):
        timeseries = {}
        for dated in self.dates:
            daily_data = self.actuals_timeseries.get(dated, {})
            timeseries[dated] = daily_data.get('hospitalBeds')
        return timeseries

    @property
    def icu_beds(self):
        timeseries = {}
        for dated in self.dates:
            daily_data = self.actuals_timeseries.get(dated, {})
            timeseries[dated] = daily_data.get('icuBeds')
        return timeseries

    #
    # Instance Methods
    #
    def __init__(self, **keywords):
        self.fips = keywords.get("fips")

    #
    # Private
    #

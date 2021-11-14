import csv
import requests
import codecs
from contextlib import closing
from datetime import datetime
from functools import cached_property


EXTRACT_URL = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
DATE_F = '%Y-%m-%d'
OC_FIPS = '06059'
KENT_MI_FIPS = '26081'


class NyTimesCovid19Extract:
    #
    # Static Methods
    #
    @staticmethod
    def kent_mi_daily_extract():
        """Returns instance of extract.
        """
        extract = NyTimesCovid19Extract(fips=KENT_MI_FIPS)
        return extract

    @staticmethod
    def oc_daily_deaths():
        """Returns a dict: {date: count, ...} for Orange County, CA.
        """
        extract = NyTimesCovid19Extract()
        source_stream = extract.fetch_source_stream()
        data = extract.filter_oc_deaths(source_stream)
        return data

    #
    # Properties
    #
    @cached_property
    def daily_logs(self):
        return self.fetch_data_source()

    #
    # Instance Methods
    #
    def __init__(self, fips=None):
        self.url = EXTRACT_URL
        self.fips = fips
        self.json = None

    def fetch_data_source(self):
        daily_values = {}

        response = requests.get(self.url, stream=True)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error

        # Large stream pattern: https://stackoverflow.com/a/38677650/1093087
        with closing(response) as r:
            str_iterator = codecs.iterdecode(r.iter_lines(), 'utf-8')
            reader = csv.reader(str_iterator, delimiter=',', quotechar='"')
            last_data_row = (None, 0, 0, 0, 0)

            for row in reader:
                date_str, county, state, fips, total_cases, total_deaths = row

                if fips != self.fips:
                    continue

                dated = datetime.strptime(date_str, DATE_F).date()
                total_cases = int(total_cases)
                total_deaths = int(total_deaths)
                new_cases = total_cases - last_data_row[1]
                new_deaths = total_deaths - last_data_row[2]

                daily_log = {
                    'date': dated,
                    'new_cases': new_cases,
                    'new_deaths': new_deaths,
                    'total_cases': total_cases,
                    'total_deaths': total_deaths
                }

                last_data_row = (dated, total_cases, total_deaths, new_cases, new_deaths)
                daily_values[dated] = daily_log

        return daily_values

    def extract_daily_log(self, row):
        date_str, county, state, fips, total_cases, total_deaths = row

        if fips != self.fips:
            return None

        dated = datetime.strptime(date_str, DATE_F).date()
        total_cases = int(total_cases)
        total_deaths = int(total_deaths)
        new_cases = total_cases - last_data_row[1]
        new_deaths = total_deaths - last_data_row[2]

        daily_log = {
            'date': dated,
            'new_cases': new_cases,
            'new_deaths': new_deaths,
            'total_cases': total_cases,
            'total_deaths': total_deaths
        }

        return daily_log

    def extract_from_daily_logs(self, field_key, data_type=str):
        daily_values = {}

        for dated in self.daily_logs:
            daily_log = self.daily_logs[dated]
            value = daily_log[field_key]

            try:
                daily_values[dated] = data_type(value)
            except TypeError:
                daily_values[dated] = None

        return daily_values

    def fetch_source_stream(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()     # If error, will raise a requests.exceptions.HTTPError
        return response

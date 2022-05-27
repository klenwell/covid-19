import csv
import requests
import codecs
from contextlib import closing
from datetime import datetime
from functools import cached_property


EXTRACT_URL_F = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-{}.csv'
DATE_F = '%Y-%m-%d'
START_YEAR = 2020
KENT_MI_FIPS = '26081'


class NyTimesCountiesExtract:
    #
    # Static Methods
    #
    @staticmethod
    def kent_mi_extract():
        """Returns instance of extract.
        """
        extract = NyTimesCountiesExtract(fips=KENT_MI_FIPS)
        return extract

    #
    # Properties
    #
    @cached_property
    def daily_logs(self):
        logs = {}

        for year in self.pandemic_years:
            for dated, data in self.yearly_logs[year].items():
                logs[dated] = data

        return logs

    @cached_property
    def yearly_logs(self):
        logs = {}

        for year in self.pandemic_years:
            logs[year] = self.fetch_data_source_by_year(year)
            print(year, len(logs[year].values()))

        return logs

    @property
    def pandemic_years(self):
        num_years = datetime.today().year - START_YEAR
        for n in range(num_years + 1):
            year = START_YEAR + n
            yield year

    #
    # Instance Methods
    #
    def __init__(self, fips):
        self.fips = fips

    def fetch_data_source_by_year(self, year):
        daily_values = {}
        source_url = EXTRACT_URL_F.format(year)
        print('fetch {}...'.format(source_url))

        # Large stream pattern: https://stackoverflow.com/a/38677650/1093087
        stream = self.fetch_source_stream(source_url)
        with closing(stream) as r:
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

    def fetch_source_stream(self, url):
        response = requests.get(url, stream=True)
        response.raise_for_status()     # If error, will raise a requests.exceptions.HTTPError
        return response

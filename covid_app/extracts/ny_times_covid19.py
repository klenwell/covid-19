import csv
import requests
import codecs
from contextlib import closing
from datetime import datetime


EXTRACT_URL = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
DATE_F = '%Y-%m-%d'
OC_FIPS = '06059'
KENT_MI_FIPS = '26081'


class NyTimesCovid19Extract:
    #
    # Static Methods
    #
    @staticmethod
    def oc_daily_deaths():
        """Returns a dict: {date: count, ...} for Orange County, CA.
        """
        extract = NyTimesCovid19Extract()
        source_stream = extract.fetch_source_stream()
        data = extract.filter_oc_deaths(source_stream)
        return data

    #
    # Instance Methods
    #
    def __init__(self):
        self.url = EXTRACT_URL

    def filter_oc_deaths(self, source_stream):
        """Returns a dict: {date: count, ...}
        """
        # Large stream pattern: https://stackoverflow.com/a/38677650/1093087
        with closing(source_stream) as r:
            str_iterator = codecs.iterdecode(r.iter_lines(), 'utf-8')
            reader = csv.reader(str_iterator, delimiter=',', quotechar='"')
            oc_rows = []
            last_count = 0

            for row in reader:
                date_str, _, _, fips, _, total_deaths = row

                if fips != OC_FIPS:
                    continue

                date = datetime.strptime(date_str, DATE_F).date()
                total_count = int(total_deaths)
                daily_count = total_count - last_count

                oc_rows.append([date, daily_count, total_count])
                last_count = total_count

        oc_deaths = dict([(row[0], row[1]) for row in oc_rows])
        return oc_deaths

    def filter_kent_mi_data(self, source_stream):
        """Returns a list of daily data.
        """
        # Large stream pattern: https://stackoverflow.com/a/38677650/1093087
        with closing(source_stream) as r:
            str_iterator = codecs.iterdecode(r.iter_lines(), 'utf-8')
            reader = csv.reader(str_iterator, delimiter=',', quotechar='"')
            kent_data = []
            last_data_row = (None, 0, 0, 0, 0)

            for row in reader:
                date_str, county, state, fips, total_cases, total_deaths = row

                if fips != KENT_MI_FIPS:
                    continue

                date = datetime.strptime(date_str, DATE_F).date()
                total_cases = int(total_cases)
                total_deaths = int(total_deaths)
                new_cases = total_cases - last_data_row[1]
                new_deaths = total_deaths - last_data_row[2]

                new_data_row = (date, total_cases, total_deaths, new_cases, new_deaths)
                kent_data.append(new_data_row)
                last_data_row = new_data_row

        return kent_data

    def fetch_source_stream(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()     # If error, will raise a requests.exceptions.HTTPError
        return response

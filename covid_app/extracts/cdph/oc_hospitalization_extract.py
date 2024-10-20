"""
CA Department of Hospitalization Extract

For info on data source, see:
https://data.ca.gov/dataset/covid-19-hospital-data1

To test or troubleshoot (see main block at bottom of file):

    $ python covid_app/extracts/cdph/oc_hospitalization_extract.py [--live]
"""
import sys
import requests
import csv
import codecs
import time
from os.path import dirname, abspath, join as path_join
from functools import cached_property
from datetime import datetime, timedelta
from contextlib import closing


EXTRACT_URL = 'https://data.chhs.ca.gov'
EXTRACT_PATH_F = 'dataset/{}/resource/{}/download/{}'
DATASET_ID = '2df3e19e-9ee4-42a6-a087-9761f82033f6'
RESOURCE_ID = '47af979d-8685-4981-bced-96a6b79d3ed5'
CSV_FILE = 'covid19hospitalbycounty.csv'

ROOT_DIR = dirname(dirname(dirname(dirname(abspath(__file__)))))
SAMPLE_DATA_DIR = path_join(ROOT_DIR, 'data/samples')
SAMPLE_DATA_FILE = 'covid19hospitalbycounty.csv'

EXTRACT_COUNTY = 'Orange'
DATE_FORMAT = '%Y-%m-%d'


class DataSourceError(Exception):
    pass


class OcHospitalDataExtract:
    #
    # Properties
    #
    # Data Source Info
    @property
    def url(self):
        extract_path = EXTRACT_PATH_F.format(DATASET_ID, RESOURCE_ID, CSV_FILE)
        return path_join(EXTRACT_URL, extract_path)

    @property
    def sample_csv_path(self):
        return path_join(SAMPLE_DATA_DIR, SAMPLE_DATA_FILE)

    # Data
    @cached_property
    def csv_rows(self):
        """This property triggers call to CDPH site. It's expensive.
        """
        if self.use_mock:
            return self.load_test_csv()

        # Large stream pattern: https://stackoverflow.com/a/38677650/1093087
        rows = []
        stream = self.fetch_source_stream()

        with closing(stream) as r:
            str_iterator = codecs.iterdecode(r.iter_lines(), 'utf-8')
            reader = csv.DictReader(str_iterator)
            for row in reader:
                rows.append(row)

        if len(rows) < 10:
            f = "{} rows in file.\n\nSource can be manually checked at:\n{}"
            raise DataSourceError(f.format(len(rows), self.url))

        return rows

    @cached_property
    def hospitalizations(self):
        dated_counts = {}
        hospital_header = 'hospitalized_covid_confirmed_patients'

        for row in self.oc_rows:
            value = row[hospital_header]
            count = value if value != '' else 0
            dated_counts[row['date']] = int(float(count))

        return dated_counts

    @cached_property
    def icu_cases(self):
        dated_counts = {}
        icu_header = 'icu_covid_confirmed_patients'

        for row in self.oc_rows:
            value = row[icu_header]
            count = value if value != '' else 0
            dated_counts[row['date']] = int(float(count))

        return dated_counts

    @cached_property
    def oc_rows(self):
        rows = []
        county_header = 'county'
        date_header = 'todays_date'

        for row in self.csv_rows:
            county = row.get(county_header)
            date = row[date_header]

            # Collect only OC rows
            if county.lower() != EXTRACT_COUNTY.lower():
                continue

            row['date'] = self.date_str_to_date(date)
            rows.append(row)

        return rows

    # Dates
    @cached_property
    def report_dates(self):
        dates = []
        for row in self.oc_rows:
            dates.append(row['date'])
        return sorted(list(set(dates)))

    @cached_property
    def dates(self):
        dates = []

        # Fencepost alert: Don't forget to add one to range to include final day.
        for n in range(int((self.ends_on - self.starts_on).days) + 1):
            date = self.starts_on + timedelta(n)
            dates.append(date)

        return dates

    @property
    def starts_on(self):
        return self.report_dates[0]

    @property
    def ends_on(self):
        return self.report_dates[-1]

    #
    # Instance Methods
    #
    def __init__(self, mock=False):
        self.use_mock = mock

    def load_test_csv(self, csv_path=None):
        rows = []

        if csv_path is None:
            csv_path = self.sample_csv_path

        print('NOTE: using mock data from sample csv: {}'.format(csv_path))
        time.sleep(1)

        with open(csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)

        return rows

    #
    # Private
    #
    def fetch_source_stream(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        return response

    def date_str_to_date(self, date_str):
        alt_format = "%m/%d/%Y"
        try:
            return datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            return datetime.strptime(date_str, alt_format).date()


#
# For testing
# python covid_app/extracts/cdph/oc_hospitalization_extract.py [--live]
#
if __name__ == "__main__":
    extract = OcHospitalDataExtract()

    if sys.argv[-1] == '--live':
        extract.use_mock = False
        print('Using live data from {}'.format(extract.url))
    else:
        extract.use_mock = True
        print("Using sample csv: {}".format(extract.sample_csv_path))

    breakpoint()

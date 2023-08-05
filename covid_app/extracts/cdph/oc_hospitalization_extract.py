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
import math
import time
from os.path import dirname, abspath, join as path_join
from functools import cached_property
from datetime import datetime, timedelta
from contextlib import closing


EXTRACT_URL = 'https://data.chhs.ca.gov'
EXTRACT_PATH_F = '/dataset/{}/resource/{}/download/{}'
DATASET_ID = '2df3e19e-9ee4-42a6-a087-9761f82033f6'
RESOURCE_ID = '47af979d-8685-4981-bced-96a6b79d3ed5'
CSV_FILE = 'covid19hospitalbycounty.csv'
START_DATE = '6/28/2021'

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
            dated_counts[row['date']] = row[hospital_header]

        return dated_counts

    @cached_property
    def icu_patients(self):
        dated_counts = {}
        icu_header = 'icu_covid_confirmed_patients'

        for row in self.oc_rows:
            dated_counts[row['date']] = row[icu_header]

        return dated_counts

    @cached_property
    def hospitalization_7d_avgs(self):
        dated_counts = {}
        dated_pre_samples = {}

        for row in self.cal3_rows:
            if row['Ten Rollapply'] != '':
                dated_pre_samples[row['date']] = row

        # Add 7-day ml avg
        for dated in self.dates:
            pre_sample = dated_pre_samples.get(dated, {})
            pre_sample['virus_ml_7d_avg'] = \
                self.compute_viral_count_7d_avg_for_date(dated, dated_pre_samples)
            dated_samples[dated] = pre_sample

        return dated_samples

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
        # Use START_DATE rather than self.report_dates[0] to avoid gaps in reporting
        #return self.date_str_to_date(START_DATE)
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

    def viral_counts_7d_avg_by_lab(self, lab):
        dataset = {}
        lab = lab.upper()
        samples = self.dwrl_samples if lab == 'DWRL' else self.cal3_samples

        for dated in self.dates:
            dataset[dated] = samples[dated]['virus_ml_7d_avg']

        return dataset

    def compute_viral_count_7d_avg_for_date(self, dated, dated_samples):
        viral_counts = []

        for days_back in range(7):
            back_date = dated - timedelta(days=days_back)
            sample = dated_samples.get(back_date, {})
            viral_count = sample.get('virus_ml')

            if viral_count:
                viral_counts.append(viral_count)

        if len(viral_counts) < 1:
            return None
        else:
            return sum(viral_counts) / len(viral_counts)

    #
    # Private
    #
    def fetch_source_stream(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        return response

    def date_str_to_date(self, date_str):
        return datetime.strptime(date_str, DATE_FORMAT).date()


#
# For testing
# python covid_app/extracts/cdph/oc_wastewater_extract.py [--live]
#
if __name__ == "__main__":
    extract = OcHospitalDataExtract()

    if sys.argv[-1] == '--live':
        extract.use_mock = False
        print('Using live data from {}'.format(extract.url))
    else:
        extract.use_mock = True
        print("Using sample csv: {}".format(extract.sample_csv_path))

    #print('Latest sample:', extract.newest_sample)
    #print('Latest OC sample:', extract.ends_on)

    breakpoint()

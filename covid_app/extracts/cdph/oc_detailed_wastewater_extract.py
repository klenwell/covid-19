"""
CA Department of Wastewater Extract

For info on data source, see:
https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/COVID-19/CalSuWers-Dashboard.aspx
"""
import requests
import csv
import codecs
import math
import time
from os.path import join as path_join
from functools import cached_property
from datetime import datetime, timedelta
from contextlib import closing
from config.app import DATA_ROOT, OC_FIPS


DATASET_ID = 'b8c6ee3b-539d-4d62-8fa2-c7cd17c16656'
RESOURCE_ID = '16bb2698-c243-4b66-a6e8-4861ee66f8bf'
EXTRACT_URL = 'https://data.ca.gov'
EXTRACT_URL_F = "{}/dataset/{}/resource/{}/download/master-covid-public.csv"
SAMPLE_CSV = 'cdph-master-wastewater.csv'
START_DATE = '6/28/2021'


class DataSourceError(Exception):
    pass


class OcWastewaterExtract:
    #
    # Properties
    #
    # Data Source Info
    @property
    def url(self):
        return EXTRACT_URL_F.format(EXTRACT_URL, DATASET_ID, RESOURCE_ID)

    @property
    def sample_csv_path(self):
        if self.csv_path is None:
            return path_join(DATA_ROOT, 'samples', SAMPLE_CSV)
        else:
            return self.csv_path

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
    def oc_rows(self):
        rows = []
        county_header = 'county_names'
        county_filter = OC_FIPS
        virus_type_header = 'pcr_target'
        virus_type_filter = 'sars-cov-2'

        for row in self.csv_rows:
            date = row['sample_collect_date']
            concentrate = row.get('pcr_target_avg_conc', '0.0')
            county_value = row.get(county_header)
            virus_type_value = row.get(virus_type_header)
            is_oc = county_value == county_filter
            is_covid = virus_type_value == virus_type_filter

            # Data source includes all CA counties and readings for other viruses like
            # Norovirus and RSV. Collect only rows for OC and Covid.
            if not (is_oc and is_covid):
                continue

            row['date'] = self.date_str_to_date(date)
            row['virus'] = int(round(float(concentrate.replace(',', ''))))
            row['virus_ml'] = row['virus'] / 1000

            if row['virus'] > 0:
                row['log_virus'] = math.log(row['virus'])
                rows.append(row)

        return rows

    # Identifiers
    @property
    def zip_codes(self):
        return set([r['zipcode'] for r in self.oc_rows])

    @property
    def all_zip_codes(self):
        return set([r['zipcode'] for r in self.csv_rows])

    @property
    def sites(self):
        sites = []
        for row in self.oc_rows:
            site_group = (
                ('site_id', row['site_id']),
                ('zipcode', row['zipcode']),
                ('epaid', row['epaid']),
                ('wwtp_name', row['wwtp_name']),
                ('county_names', row['county_names'])
            )
            sites.append(site_group)
        return set(sites)

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
        return self.date_str_to_date(START_DATE)

    @property
    def ends_on(self):
        return self.report_dates[-1]

    #
    # Instance Methods
    #
    def __init__(self, mock=False, csv_path=None):
        self.use_mock = mock
        self.csv_path = csv_path

    def load_test_csv(self):
        rows = []

        print('NOTE: using mock data from sample csv: {}'.format(self.sample_csv_path))
        time.sleep(1)

        with open(self.sample_csv_path) as csvfile:
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
        """date_str will have format like: 2/1/2022 12:00:00 AM
        """
        format = '%m/%d/%Y'
        date_sub = date_str.split(' ')[0]

        try:
            return datetime.strptime(date_sub, format).date()
        except ValueError:
            print("date value error:", date_sub)
            return datetime.strptime(date_sub, '%Y-%m-%d').date()

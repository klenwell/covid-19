"""
CA Department of Wastewater Extract

For info on data source, see:
https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/COVID-19/CalSuWers-Dashboard.aspx
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


DATASET_ID = 'b8c6ee3b-539d-4d62-8fa2-c7cd17c16656'
RESOURCE_ID = '16bb2698-c243-4b66-a6e8-4861ee66f8bf'
EXTRACT_URL = 'https://data.ca.gov'
EXTRACT_CO = 'Orange'
EXTRACT_URL_F = "{}/dataset/{}/resource/{}/download/master-covid-public.csv"
SAMPLE_CSV = 'data/samples/cdph-master-wastewater.csv'
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
        root_dir = dirname(dirname(dirname(dirname(abspath(__file__)))))
        return path_join(root_dir, SAMPLE_CSV)

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
    def cal3_samples(self):
        dated_samples = {}
        dated_pre_samples = {}

        # This used to be used to filter out duplicate or empty rows.
        for row in self.cal3_rows:
            dated_pre_samples[row['date']] = row

        # Add 7-day ml avg
        for dated in self.dates:
            pre_sample = dated_pre_samples.get(dated, {})
            pre_sample['virus_ml_7d_avg'] = \
                self.compute_viral_count_7d_avg_for_date(dated, dated_pre_samples)
            dated_samples[dated] = pre_sample

        return dated_samples

    @cached_property
    def dwrl_samples(self):
        dated_samples = {}
        dated_pre_samples = {}

        for row in self.dwrl_rows:
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
        zip_header = 'zipcode'
        county_zip = 92708

        for row in self.csv_rows:
            zipcode = row.get(zip_header)
            date = row['sample_collect_date']
            concentrate = row.get('pcr_target_avg_conc', '0.0')

            # Collect only OC rows
            if int(zipcode) != county_zip:
                continue

            row['date'] = self.date_str_to_date(date)
            row['virus'] = int(round(float(concentrate.replace(',', ''))))
            row['virus_ml'] = row['virus'] / 1000

            if row['virus'] > 0:
                row['log_virus'] = math.log(row['virus'])
                rows.append(row)

        return rows

    @cached_property
    def cal3_rows(self):
        return [row for row in self.oc_rows if row['lab_id'].upper() == 'CAL3']

    @cached_property
    def dwrl_rows(self):
        return [row for row in self.oc_rows if row['lab_id'].upper() == 'DWRL']

    # Lab Info
    @cached_property
    def lab_samples(self):
        labs = {}
        lab_header = 'lab_id'
        for row in self.oc_rows:
            lab = row.get(lab_header)
            if lab in labs:
                labs[lab].append(row)
            else:
                labs[lab] = [row]
        return labs

    @cached_property
    def lab_counts(self):
        counts = {}
        for lab, samples in self.lab_samples.items():
            counts[lab] = len(samples)
        return counts

    @cached_property
    def oc_labs(self):
        return self.lab_counts.keys()

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

    @cached_property
    def newest_samples(self):
        cal3_rows = [(r['date'], r) for r in self.cal3_rows]
        dwrl_rows = [(r['date'], r) for r in self.dwrl_rows]

        sorted_cal3_rows = sorted(cal3_rows, key=lambda r: r[0])
        sorted_dwrl_rows = sorted(dwrl_rows, key=lambda r: r[0])

        return {
            'CAL3': sorted_cal3_rows[-1] if len(sorted_cal3_rows) > 0 else None,
            'DWRL': sorted_dwrl_rows[-1] if len(sorted_dwrl_rows) > 0 else None
        }

    @cached_property
    def lab_range(self):
        cal3_dates = sorted([r['date'] for r in self.cal3_rows])
        dwrl_dates = sorted([r['date'] for r in self.dwrl_rows])

        cal3_count = len(cal3_dates)
        dwrl_count = len(dwrl_dates)

        return {
            'CAL3': (cal3_dates[0], cal3_dates[-1], cal3_count) if cal3_count > 0 else None,
            'DWRL': (dwrl_dates[0], dwrl_dates[-1], dwrl_count) if dwrl_count > 0 else None
        }

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

    def latest_update_by_lab(self, lab):
        lab = lab.upper()
        lab_data = self.newest_samples.get(lab)

        if not lab_data:
            return None
        else:
            return lab_data[0]

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
        """date_str will have format like: 2/1/2022 12:00:00 AM
        """
        format = '%m/%d/%Y'
        date_sub = date_str.split(' ')[0]
        return datetime.strptime(date_sub, format).date()

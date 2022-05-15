"""
CA Department of Wastewater Extract

For info on data source, see:
https://www.cdph.ca.gov/Programs/CID/DCDC/Pages/COVID-19/CalSuWers-Dashboard.aspx

To test or troubleshoot (see main block at bottom of file):

    $ python covid_app/extracts/cdph/oc_wastewater_extract.py [--live]
"""
import sys
import requests
import csv
import codecs
import math
from os.path import dirname, abspath, join as path_join
from functools import cached_property
from datetime import datetime, timedelta
from contextlib import closing


EXTRACT_URL = 'https://datavisualization.cdph.ca.gov'
EXTRACT_PATH = '/t/SARSCov2/views/CalSuWersDashboard_v5_AllDataExport/Cal-SuWers.csv'
EXTRACT_CO = 'Orange'
EXTRACT_URL_F = "{}{}?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link"
START_DATE = '6/28/2021'


class OcWastewaterExtract:
    #
    # Properties
    #
    @property
    def url(self):
        return EXTRACT_URL_F.format(EXTRACT_URL, EXTRACT_PATH)

    @property
    def sample_csv_path(self):
        root_dir = dirname(dirname(dirname(dirname(abspath(__file__)))))
        return path_join(root_dir, 'data/samples/Cal-SuWers.csv')

    @cached_property
    def viral_counts_7d_avg(self):
        records = {}
        for date in self.dates:
            records[date] = self.compute_viral_count_7d_avg_for_date(date)
        return records

    @cached_property
    def viral_counts(self):
        records = {}
        for date, sample in self.dated_samples.items():
            records[date] = sample['virus']
        return records

    @cached_property
    def viral_k_counts(self):
        records = {}
        for date, sample in self.dated_samples.items():
            records[date] = sample['virus_k']
        return records

    @cached_property
    def ordered_viral_counts(self):
        return sorted([(d, s['virus_k']) for (d, s) in self.dated_samples.items()])

    @cached_property
    def dated_samples(self):
        dated_samples = {}
        for row in self.cal3_rows:
            dated_samples[row['date']] = row
        return dated_samples

    @cached_property
    def csv_rows(self):
        if self.test_csv_rows:
            return self.test_csv_rows

        # Large stream pattern: https://stackoverflow.com/a/38677650/1093087
        rows = []
        stream = self.fetch_source_stream()

        with closing(stream) as r:
            str_iterator = codecs.iterdecode(r.iter_lines(), 'utf-8')
            reader = csv.DictReader(str_iterator)
            for row in reader:
                rows.append(row)

        return rows

    @cached_property
    def oc_rows(self):
        rows = []
        county_header = 'Wwtp Name'

        for row in self.csv_rows:
            county = row.get(county_header)
            date = row['Sample Date']
            concentrate = row.get('Concentration', '0.0')

            # Collect only OC rows
            if county.lower() != EXTRACT_CO.lower():
                continue

            row['date'] = self.date_str_to_date(date)
            row['virus'] = int(round(float(concentrate.replace(',', ''))))
            row['virus_k'] = row['virus'] / 1000

            if row['virus'] > 0:
                row['log_virus'] = math.log(row['virus'])
                rows.append(row)

        return rows

    @cached_property
    def cal3_rows(self):
        return [row for row in self.oc_rows if row['Lab Id'] == 'CAL3']

    @cached_property
    def lab_samples(self):
        labs = {}
        lab_header = 'Lab Id'
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

    @cached_property
    def report_dates(self):
        dates = []
        for row in self.cal3_rows:
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
    def newest_sample(self):
        csv_rows = [(self.date_str_to_date(r['Sample Date']), r) for r in self.csv_rows]
        sorted_rows = sorted(csv_rows, key=lambda r: r[0])
        return sorted_rows[-1]

    #
    # Instance Methods
    #
    def __init__(self):
        self.test_csv_rows = None

    def load_test_csv(self, csv_path=None):
        self.test_csv_rows = []

        if csv_path is None:
            csv_path = self.sample_csv_path

        with open(csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.test_csv_rows.append(row)

        return csv_path

    def compute_viral_count_7d_avg_for_date(self, dated):
        viral_counts = []

        for days_back in range(7):
            back_date = dated - timedelta(days=days_back)
            viral_count = self.viral_k_counts.get(back_date)

            if viral_count:
                viral_counts.append(viral_count)

        if len(viral_counts) < 1:
            return None
        else:
            avg_count = sum(viral_counts) / len(viral_counts)
            return int(round(avg_count))

    #
    # Private
    #
    def fetch_source_stream(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        return response

    def date_str_to_date(self, date_str):
        format = '%m/%d/%Y'
        return datetime.strptime(date_str, format).date()


#
# For testing
# python covid_app/extracts/cdph/oc_wastewater_extract.py [--live]
#
if __name__ == "__main__":
    extract = OcWastewaterExtract()

    if sys.argv[-1] == '--live':
        print('Using live data from {}'.format(extract.url))
    else:
        extract.load_test_csv()
        print("Using sample csv: {}".format(extract.sample_csv_path))

    print('Latest sample:', extract.newest_sample)
    print('Latest OC sample:', extract.ends_on)

    breakpoint()

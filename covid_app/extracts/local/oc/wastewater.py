"""
Local Daily CSPH Wastewater Extract

csv source: data/oc/oc-wastewater.csv
"""
import csv
from os.path import join as path_join
from functools import cached_property
from datetime import datetime, timedelta

from config.app import DATA_ROOT


DATE_F = '%Y-%m-%d'
START_DATE = '6/28/2021'

# This is the Site ID for the default reference dataset
# Laguna Niguel (Coastal): 06059-001-01-00-00
# Laguna Niguel (Regional): 06059-001-02-00-00
# Dana Point: 06059-002-01-00-00
REF_SITE_ID = '06059-002-01-00-00'


class OcWastewaterExtract:
    #
    # Properties
    #
    # Source Data
    @cached_property
    def export_rows(self):
        rows = []
        with open(self.csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if self.site_id == row['Site ID']:
                    rows.append(row)
        return rows

    @cached_property
    def dated_export_rows(self):
        export_rows = {}
        for row in self.export_rows:
            row['virus_ml'] = self.to_f(row['Virus/ml'])
            dated = datetime.strptime(row['Date'], DATE_F).date()
            export_rows[dated] = row
        return export_rows

    # Primary Dataset
    @cached_property
    def dataset(self):
        dated_records = {}

        # Add 7-day ml avg
        for dated in self.dates:
            row = self.dated_export_rows.get(dated, {})
            virus_7d_avg = self.compute_viral_count_7d_avg_for_date(dated, self.dated_export_rows)
            row['avg_virus_7d'] = self.to_f(virus_7d_avg)
            dated_records[dated] = row

        return dated_records

    @cached_property
    def viral_counts_7d_avg(self):
        dataset = {}

        for dated in self.dates:
            dataset[dated] = self.dataset[dated]['avg_virus_7d']

        return dataset

    # Data Source
    # I'm extracting data from an export csv.
    @cached_property
    def csv_path(self):
        fname = 'oc-wastewater.csv'
        return path_join(DATA_ROOT, 'oc', fname)

    # Dates
    @cached_property
    def dates(self):
        dates = []

        # Fencepost alert: Don't forget to add one to range to include final day.
        for n in range(int((self.end_date - self.start_date).days) + 1):
            date = self.start_date + timedelta(n)
            dates.append(date)

        return dates

    @property
    def end_date(self):
        return self.row_dates[-1]

    @property
    def start_date(self):
        return self.row_dates[0]

    @cached_property
    def row_dates(self):
        dates = []
        for row in self.export_rows:
            dated = datetime.strptime(row['Date'], DATE_F).date()
            dates.append(dated)
        return sorted(dates)

    @cached_property
    def latest_update(self):
        for dated in sorted(self.dates, reverse=True):
            if self.dataset.get(dated, {}).get('virus_ml'):
                return dated

    #
    # Instance Methods
    #
    def __init__(self, site_id=None):
        if site_id:
            self.site_id = site_id
        else:
            self.site_id = REF_SITE_ID

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

    def to_f(self, value):
        if value is None or value == '':
            return None
        else:
            return float(value)

    def to_i(self, value):
        if value is None or value == '':
            return None
        else:
            return int(value)

"""
Local Daily CSPH Wastewater Extract

csv source: data/oc/oc-wastewater.csv
"""
import csv
from os.path import join as path_join
from functools import cached_property
from datetime import datetime

from config.app import DATA_ROOT


DATE_F = '%Y-%m-%d'


class OcWastewaterExtract:
    #
    # Properties
    #
    # Source Data
    @cached_property
    def export_rows(self):
        with open(self.csv_path, newline='') as f:
            # Can't use DictReader because column names repeat.
            reader = csv.reader(f)

            # Skip column row
            rows = list(reader)[1:]
        return rows

    @cached_property
    def dated_export_rows(self):
        export_rows = {}
        for row in self.export_rows:
            dated = datetime.strptime(row[0], DATE_F).date()
            export_rows[dated] = row
        return export_rows

    # Export Datasets
    # Map dates to dated_values.
    #
    @cached_property
    def dwrl(self):
        dated_records = {}
        av7d_idx = 9
        vpml_idx = 10
        vpl_idx = 12

        for dated in self.dates:
            row = self.dated_export_rows[dated]
            record = {
                'avg_virus_7d': self.to_f(row[av7d_idx]),
                'virus_ml': self.to_f(row[vpml_idx]),
                'virus_l': self.to_i(row[vpl_idx])
            }
            dated_records[dated] = record

        return dated_records

    @cached_property
    def cal3(self):
        dated_records = {}
        av7d_idx = 1
        vpml_idx = 2
        vpl_idx = 6

        for dated in self.dates:
            row = self.dated_export_rows[dated]
            record = {
                'avg_virus_7d': self.to_f(row[av7d_idx]),
                'virus_ml': self.to_f(row[vpml_idx]),
                'virus_l': self.to_i(row[vpl_idx])
            }
            dated_records[dated] = record

        return dated_records

    # Data Source
    # I'm extracting data from an export csv.
    @cached_property
    def csv_path(self):
        fname = 'oc-wastewater.csv'
        return path_join(self.csv_dir, fname)

    @property
    def csv_dir(self):
        return path_join(DATA_ROOT, 'oc')

    # Dates
    @cached_property
    def dates(self):
        return sorted(self.row_dates)

    @property
    def end_date(self):
        return self.last_date

    @property
    def start_date(self):
        return self.first_date

    @cached_property
    def row_dates(self):
        dates = []
        for row in self.export_rows:
            dated = datetime.strptime(row[0], DATE_F).date()
            dates.append(dated)
        return sorted(dates)

    @property
    def last_date(self):
        return self.row_dates[-1]

    @property
    def first_date(self):
        return self.row_dates[0]

    @cached_property
    def newest_samples(self):
        newest = {
            'CAL3': None,
            'DWRL': None
        }

        for dated in sorted(self.dates, reverse=True):
            cal3_sample = self.cal3.get(dated, {}).get('virus_l') is not None
            dwrl_sample = self.dwrl.get(dated, {}).get('virus_l') is not None

            if newest['CAL3'] is None and cal3_sample:
                newest['CAL3'] = dated

            if newest['DWRL'] is None and dwrl_sample:
                newest['DWRL'] = dated

            if newest['CAL3'] is not None and newest['DWRL'] is not None:
                break

        return newest

    #
    # Instance Methods
    #
    def latest_update_by_lab(self, lab):
        lab = lab.upper()
        return self.newest_samples[lab]

    def viral_counts_7d_avg_by_lab(self, lab):
        dataset = {}
        lab = lab.upper()
        samples = self.dwrl if lab == 'DWRL' else self.cal3

        for dated in self.dates:
            dataset[dated] = samples[dated]['avg_virus_7d']

        return dataset

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

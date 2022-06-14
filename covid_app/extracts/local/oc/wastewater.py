"""
Local Daily CSPH Wastewater Extract

csv source: data/oc/oc-wastewater.csv
"""
import csv
from os.path import join as path_join, exists as path_exists
from functools import cached_property
from datetime import datetime, timedelta

from config.app import DATA_ROOT
from covid_app.exports.oc_wastewater import CSV_HEADER
from covid_app.extracts.cdph.oc_wastewater_extract import START_DATE


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
        dated_record = {}
        av7d_idx = 9
        vpml_idx = 10
        vpl_idx = 12

        for dated in self.dates:
            row = self.dated_export_rows[dated]
            record = {
                'avg_virus_7d': row[av7d_idx],
                'virus_ml': row[vpml_idx],
                'virus_l': row[vpl_idx]
            }
            dated_record[dated] = record

        return dated_record

    @cached_property
    def cal3(self):
        dated_record = {}
        av7d_idx = 1
        vpml_idx = 2
        vpl_idx = 6

        for dated in self.dates:
            row = self.dated_export_rows[dated]
            record = {
                'avg_virus_7d': row[av7d_idx],
                'virus_ml': row[vpml_idx],
                'virus_l': row[vpl_idx]
            }
            dated_record[dated] = record

        return dated_record

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

    #
    # Instance Methods
    #

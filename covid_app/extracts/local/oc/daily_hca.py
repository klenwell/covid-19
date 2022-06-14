"""
Local Daily OC HCA Extract

csv source: data/oc/daily/oc-hca-YYYYmmdd.csv

The daily extract is a Jenkins job that is run nightly. So that data may be more timely
than the manually run oc-hca.csv. It also has a slightly different format.
"""
import csv
from os.path import join as path_join, exists as path_exists
from functools import cached_property
from datetime import datetime, timedelta

from config.app import DATA_ROOT


DATE_F = '%Y-%m-%d'
START_DATE = '2020-03-05'

# Export column names
# This should match column names in datasource file
COL_NAMES = {
    'tests_admin': 'New Tests Administered',
    'tests_positive': 'Pos Tests Administered',
    'new_cases': 'New Cases',
    'hospitalizations': 'Hospitalizations',
    'icu_cases': 'ICU',
    'deaths': 'New Deaths'
}


class OcDailyHcaExtract:
    #
    # Properties
    #
    # Source Data
    @cached_property
    def export_rows(self):
        with open(self.csv_path, newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows

    @cached_property
    def dated_export_rows(self):
        export_rows = {}
        for row in self.export_rows:
            dated = datetime.strptime(row['Date'], DATE_F).date()
            export_rows[dated] = row
        return export_rows

    # Export Datasets
    # Map dates to dated_values.
    #
    @cached_property
    def tests_admin(self):
        return self.extract_timeseries_by_column(COL_NAMES['tests_admin'])

    @cached_property
    def tests_positive(self):
        return self.extract_timeseries_by_column(COL_NAMES['tests_positive'])

    @cached_property
    def new_cases(self):
        return self.extract_timeseries_by_column(COL_NAMES['new_cases'])

    @cached_property
    def hospitalizations(self):
        return self.extract_timeseries_by_column(COL_NAMES['hospitalizations'])

    @cached_property
    def icu_cases(self):
        return self.extract_timeseries_by_column(COL_NAMES['icu_cases'])

    @cached_property
    def deaths(self):
        return self.extract_timeseries_by_column(COL_NAMES['deaths'])

    @cached_property
    def avg_positive_rates(self):
        dated_values = {}

        for dated in self.dates:
            tests = []
            positives = []
            for days_back in range(7):
                prev_date = dated - timedelta(days=days_back)
                tests.append(self.tests_admin[prev_date])
                positives.append(self.tests_positive[prev_date])
            dated_values[dated] = sum(positives) / sum(tests) * 100

        return dated_values

    @cached_property
    def avg_new_cases(self):
        dated_values = {}

        for dated in self.dates:
            cases = []
            for days_back in range(7):
                prev_date = dated - timedelta(days=days_back)
                cases.append(self.new_cases[prev_date])
            dated_values[dated] = sum(cases) / len(cases)

        return dated_values

    # Data Source
    # I'm extracting data from an export csv.
    @cached_property
    def csv_path(self):
        fname_f = 'oc-hca-{}.csv'

        # Find latest file by date in directory, going backwards from today
        today = datetime.now().date()
        for days_back in range(3):
            dated = today - timedelta(days=days_back)
            fname = fname_f.format(dated.strftime('%Y%m%d'))
            fpath = path_join(self.csv_dir, fname)
            if path_exists(fpath):
                return fpath

        raise ValueError('Could not find file.')

    @property
    def csv_dir(self):
        return path_join(DATA_ROOT, 'oc', 'daily')

    # Dates
    @cached_property
    def dates(self):
        num_days = (self.end_date - self.start_date).days
        return [self.start_date + timedelta(days=n) for n in range(num_days + 1)]

    @property
    def end_date(self):
        col = COL_NAMES
        for row in self.export_rows:
            try:
                int(row[col['tests_admin']]) and int(row[col['tests_positive']])
                return datetime.strptime(row['Date'], DATE_F).date()
            except ValueError:
                pass

    @property
    def start_date(self):
        return datetime.strptime(START_DATE, DATE_F).date()

    @property
    def row_dates(self):
        dates = []
        for row in self.export_rows:
            dated = datetime.strptime(row['Date'], DATE_F).date()
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
    def extract_timeseries_by_column(self, col_name, value_callback=int):
        dated_values = {}
        for dated in self.dated_export_rows.keys():
            try:
                value = self.dated_export_rows[dated][col_name]
                value = value_callback(value) if value_callback(value) is not None else value
                dated_values[dated] = value
            except ValueError:
                pass
        return dated_values

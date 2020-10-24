"""
DailyArchiveExtract

Extract data from daily archive files.
"""
#
# Imports
#
from os.path import join as path_join
from datetime import datetime, timedelta
from functools import cached_property
import csv
from statistics import stdev

from config.app import DATA_ROOT


#
# Constants
#
OC_DATA_PATH = path_join(DATA_ROOT, 'oc')


#
# Classes
#
class OcDailyArchiveExtract:
    #
    # CSV Data
    #
    @cached_property
    def csv_rows(self):
        with open(self.file_path, newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        return rows

    @cached_property
    def header(self):
        return self.csv_rows[0]

    @cached_property
    def data_rows(self):
        return self.csv_rows[1:]

    @cached_property
    def dated_rows(self):
        dated_rows = {}
        for row in self.data_rows:
            dated = datetime.strptime(row[0], '%Y-%m-%d').date()
            dated_rows[dated] = row
        return dated_rows

    #
    # Dates
    #
    @cached_property
    def dates(self):
        return self.dated_rows.keys()

    @cached_property
    def previous_date(self):
        return self.date - timedelta(days=1)

    #
    # Delays
    #
    @property
    def average_test_delay(self):
        delayed_days = []
        total_tests = []

        for dated, count in self.increased_admin_tests.items():
            days = (self.date - dated).days
            delayed_days.append(days * count)
            total_tests.append(count)

        return sum(delayed_days) / sum(total_tests)

    @property
    def delays_as_list(self):
        test_delays = []

        for dated, count in self.increased_admin_tests.items():
            days = (self.date - dated).days
            daily_test_delays = [days] * count
            test_delays += daily_test_delays

        return test_delays

    @property
    def test_delay_stdev(self):
        return stdev(self.delays_as_list)

    @property
    def oldest_updated_admin_test(self):
        test_dates = self.increased_admin_tests.keys()
        return min(test_dates)

    #
    # Test Counts
    #
    @cached_property
    def dated_reported_new_tests(self):
        CSV_COL = 3
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[CSV_COL]
        return dated_tests

    @property
    def reported_new_tests(self):
        # Repo tests come a day late
        return self.dated_reported_new_tests.get(self.previous_date)

    @property
    def reported_total_admin_tests(self):
        return sum(self.updated_admin_tests.values())

    @cached_property
    def admin_tests(self):
        CSV_COL = 1
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[CSV_COL]
        return dated_tests

    @cached_property
    def new_admin_tests(self):
        new_admin_tests = {}

        # Start with yesterday since tests are always reported a day late
        for dated in list(self.dates)[1:]:
            today = self.admin_tests.get(dated, 0) or 0
            yesterday = self.previous_date_extract.admin_tests.get(dated, 0) or 0
            change = int(today) - int(yesterday)
            new_admin_tests[dated] = change

        return new_admin_tests

    @cached_property
    def updated_admin_tests(self):
        updated_admin_tests = {}

        for dated, change in self.new_admin_tests.items():
            if change != 0:
                updated_admin_tests[dated] = change

        return updated_admin_tests

    @cached_property
    def increased_admin_tests(self):
        increased_admin_tests = {}

        for dated, change in self.updated_admin_tests.items():
            if change > 0:
                increased_admin_tests[dated] = change

        return increased_admin_tests

    @cached_property
    def decreased_admin_tests(self):
        decreased_admin_tests = {}

        for dated, change in self.updated_admin_tests.items():
            if change < 0:
                decreased_admin_tests[dated] = change

        return decreased_admin_tests

    #
    # Positive Counts
    #
    @cached_property
    def dated_reported_new_cases(self):
        CSV_COL = 4
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[CSV_COL]
        return dated_tests

    @property
    def reported_new_cases(self):
        # Repo tests come a day late
        return self.dated_reported_new_tests.get(self.previous_date)

    @property
    def reported_total_positive_tests(self):
        return sum(self.updated_positive_tests.values())

    @cached_property
    def positive_tests(self):
        CSV_COL = 2
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[CSV_COL]
        return dated_tests

    @cached_property
    def new_positive_tests(self):
        new_positive_tests = {}

        # Start with yesterday since tests are always reported a day late
        for dated in list(self.dates)[1:]:
            today = self.positive_tests.get(dated, 0) or 0
            yesterday = self.previous_date_extract.positive_tests.get(dated, 0) or 0
            change = int(today) - int(yesterday)
            new_positive_tests[dated] = change

        return new_positive_tests

    @cached_property
    def updated_positive_tests(self):
        updated_positive_tests = {}

        for dated, change in self.new_positive_tests.items():
            if change != 0:
                updated_positive_tests[dated] = change

        return updated_positive_tests

    @property
    def reported_new_cases_for_yesterday(self):
        # Repo tests come a day late
        FOR_YESTERDAY = 2
        CASE_COL = 4
        return int(self.csv_rows[FOR_YESTERDAY][CASE_COL])

    #
    # Positive Rate
    #
    @property
    def reported_test_positive_rate(self):
        return self.reported_total_positive_tests / self.reported_total_admin_tests

    @property
    def reported_case_positive_rate(self):
        return self.reported_new_cases_for_yesterday / self.reported_new_tests

    #
    # 7-Day Averages
    #
    @cached_property
    def dated_7d_avg_test_specs(self):
        dated_avgs = {}

        for dated in list(self.dates):
            data_set = self.admin_tests
            avg = self.compute_7d_avg_for_data_set_on_date(data_set, dated)
            dated_avgs[dated] = avg

        return dated_avgs

    @cached_property
    def dated_7d_avg_positive_specs(self):
        dated_avgs = {}

        for dated in list(self.dates):
            data_set = self.positive_tests
            avg = self.compute_7d_avg_for_data_set_on_date(data_set, dated)
            dated_avgs[dated] = avg

        return dated_avgs

    @cached_property
    def dated_7d_avg_spec_positive_rate(self):
        dated_avgs = {}

        for dated in list(self.dates):
            tests = self.dated_7d_avg_test_specs[dated]
            positives = self.dated_7d_avg_positive_specs[dated]

            if not (tests and positives):
                dated_avgs[dated] = None
            else:
                dated_avgs[dated] = positives / tests

        return dated_avgs

    @cached_property
    def dated_7d_avg_reported_tests(self):
        dated_avgs = {}

        for dated in list(self.dates):
            data_set = self.dated_reported_new_tests
            avg = self.compute_7d_avg_for_data_set_on_date(data_set, dated)
            dated_avgs[dated] = avg

        return dated_avgs

    @cached_property
    def dated_7d_avg_new_cases(self):
        dated_avgs = {}

        for dated in list(self.dates):
            data_set = self.dated_reported_new_cases
            avg = self.compute_7d_avg_for_data_set_on_date(data_set, dated)
            dated_avgs[dated] = avg

        return dated_avgs

    @property
    def dated_7d_avg_positive_case_rate(self):
        dated_avgs = {}

        for dated in list(self.dates):
            tests = self.dated_7d_avg_reported_tests[dated]
            positives = self.dated_7d_avg_new_cases[dated]

            if not (tests and positives):
                dated_avgs[dated] = None
            else:
                dated_avgs[dated] = positives / tests

        return dated_avgs

    #
    # File Info
    #
    @property
    def file_name(self):
        yyyymmdd = self.date.strftime('%Y%m%d')
        return 'oc-hca-{}.csv'.format(yyyymmdd)

    @property
    def file_path(self):
        return path_join(OC_DATA_PATH, 'daily', self.file_name)

    #
    # Etc.
    #
    @cached_property
    def previous_date_extract(self):
        return OcDailyArchiveExtract(self.previous_date)

    #
    # Instance Methods
    #
    def __init__(self, dated):
        self.date = dated

    #
    # Private Methods
    #
    def compute_7d_avg_for_data_set_on_date(self, data_set, dated):
        counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            daily_count = data_set.get(on_date)

            if daily_count in [None, '']:
                return None

            counts.append(float(daily_count))

        return sum(counts) / len(counts)

    #
    # Magic Methods
    #
    def __repr__(self):
        return '<OcDailyDataExtract date={} rows={}>'.format(self.date, len(self.csv_rows))

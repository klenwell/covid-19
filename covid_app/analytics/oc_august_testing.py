"""
OC August 2020 Test Analysis

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import date, timedelta

from config.app import DATA_ROOT


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')

CSV_HEADER = ['DATE', '+1d', '+2d', '+3d', '+4d', '+5d', '+6d', '+7d', '+8-14d',
              '+15-30d', 'TOTAL (9/1)']


class OcDailyDataExtract:
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
    def dates(self):
        dates = []
        for row in self.data_rows:
            dates.append(row[0])
        return dates

    @cached_property
    def dated_rows(self):
        dated_rows = {}
        for row in self.data_rows:
            dated = row[0]
            dated_rows[dated] = row
        return dated_rows

    @cached_property
    def admin_tests(self):
        ADMIN_TEST_COL = 1
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[ADMIN_TEST_COL]
        return dated_tests

    def __init__(self, dated):
        self.date = dated
        self.file_name = 'oc-hca-{}.csv'.format(dated.strftime('%Y%m%d'))
        self.file_path = path_join(OC_DATA_PATH, 'daily', self.file_name)


class OcAugustTestAnalysis:
    #
    # Properties
    #
    @cached_property
    def start_date(self):
        return date(self.year, self.month, 1)

    @cached_property
    def end_date(self):
        next_month = self.month + 1
        return date(self.year, next_month, 1)

    @cached_property
    def dates(self):
        month_dates = []

        for n in range(self.days_in_month):
            dated = self.start_date + timedelta(days=n)
            month_dates.append(dated)

        return month_dates

    @cached_property
    def daily_extracts(self):
        dated_extracts = {}

        # Tests are reported next day, so we actually want to offset a day to go from
        # 2 Aug to 1 Sep.
        for dated in self.dates:
            next_day = dated + timedelta(days=1)
            extract = OcDailyDataExtract(next_day)
            dated_extracts[next_day] = extract

        return dated_extracts

    @cached_property
    def total_tests_time_series(self):
        time_series = {}
        for dated in self.dates:
            time_series[dated] = self.extract_total_tests_time_series_for_date(dated)
        return time_series

    @cached_property
    def total_positives_time_series(self):
        pass

    @cached_property
    def new_tests_time_series(self):
        pass

    @cached_property
    def new_positives_time_series(self):
        pass

    #
    # Instance Method
    #
    def __init__(self):
        self.month = 8
        self.year = 2020
        self.days_in_month = 31

    def to_csv(self):
        pass

    #
    # Private
    #
    def extract_total_tests_time_series_for_date(self, dated):
        series = []
        num_days = (self.end_date - dated).days

        for n in range(num_days):
            # Remember offset since tests are reported next day
            next_day = n + 1
            extract_date = dated + timedelta(next_day)
            extract = self.daily_extracts[extract_date]
            total_tests = extract.admin_tests.get(dated)
            series.append(total_tests)

        return series

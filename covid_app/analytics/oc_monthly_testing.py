"""
OC Monthly Testing Test Analysis

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import datetime, date, timedelta
from calendar import monthrange

from config.app import DATA_ROOT


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE_NAME_F = 'oc-test-analysis-{}-{}.csv'

CSV_HEADER = ['Date', '+1d', '+2d', '+3d', '+4d', '+5d', '+6d', '+7d', '+8-14d',
              '+15d+', 'TOTAL ({})']


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
    def dated_rows(self):
        dated_rows = {}
        for row in self.data_rows:
            dated = datetime.strptime(row[0], '%Y-%m-%d').date()
            dated_rows[dated] = row
        return dated_rows

    @cached_property
    def dates(self):
        return self.dated_rows.keys()

    @cached_property
    def admin_tests(self):
        CSV_COL = 1
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[CSV_COL]
        return dated_tests

    @cached_property
    def positive_tests(self):
        CSV_COL = 2
        dated_tests = {}
        for dated in self.dates:
            row = self.dated_rows.get(dated)
            dated_tests[dated] = row[CSV_COL]
        return dated_tests

    def __init__(self, dated):
        self.date = dated
        self.file_name = 'oc-hca-{}.csv'.format(dated.strftime('%Y%m%d'))
        self.file_path = path_join(OC_DATA_PATH, 'daily', self.file_name)

    def __repr__(self):
        return '<OcDailyDataExtract date={} rows={}>'.format(self.date, len(self.csv_rows))


class OcMonthlyTestAnalysis:
    #
    # Properties
    #
    @cached_property
    def start_date(self):
        return date(self.year, self.month, 1)

    @cached_property
    def end_date(self):
        return self.start_date + timedelta(days=self.days_in_month)

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

        for extract_date in self.extract_dates:
            extract = OcDailyDataExtract(extract_date)
            dated_extracts[extract_date] = extract

        return dated_extracts

    @cached_property
    def total_tests_time_series(self):
        time_series = {}
        for dated in self.dates:
            time_series[dated] = self.extract_total_tests_time_series_for_date(dated)
        return time_series

    @cached_property
    def new_tests_time_series(self):
        time_series = {}
        for dated in self.dates:
            time_series[dated] = self.extract_new_tests_time_series_for_date(dated)
        return time_series

    @cached_property
    def total_positives_time_series(self):
        time_series = {}
        for dated in self.dates:
            time_series[dated] = self.extract_total_positives_time_series_for_date(dated)
        return time_series

    @cached_property
    def new_positives_time_series(self):
        time_series = {}
        for dated in self.dates:
            time_series[dated] = self.extract_new_positives_time_series_for_date(dated)
        return time_series

    @property
    def days_in_month(self):
        # https://stackoverflow.com/a/4938459/1093087
        return monthrange(self.year, self.month)[-1]

    @property
    def yesterday(self):
        return date.today() - timedelta(days=1)

    @property
    def extract_dates(self):
        """Returns dates to pull extracts spanning from beginning of month requested
        to yesterday.

        Tests are reported next day, so we actually want to offset a day to go from
        second day of month to yesterday.
        """
        extract_dates = []
        num_days = (self.yesterday - self.start_date).days

        for n in range(1, num_days+1):
            dated = self.start_date + timedelta(days=n)
            extract_dates.append(dated)

        return extract_dates

    #
    # Instance Method
    #
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def to_csv(self):
        tests_csv = self.series_to_csv('tests', self.new_tests_time_series)
        positives_csv = self.series_to_csv('positives', self.new_positives_time_series)
        return [tests_csv, positives_csv]

    #
    # Private
    #
    def series_to_csv(self, name, series):
        year_month = '{}{:02}'.format(self.year, self.month)
        file_name = ANALYTICS_FILE_NAME_F.format(name, year_month)
        csv_path = path_join(OC_ANALYTICS_DATA_PATH, file_name)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                writer.writerow(self.series_data_to_csv_row(series, dated))

        return csv_path

    def series_data_to_csv_row(self, series, dated):
        dated_dataset = series[dated]
        plus_1d = self.get_series_value_by_day_offset(dated_dataset, 1)
        plus_2d = self.get_series_value_by_day_offset(dated_dataset, 2)
        plus_3d = self.get_series_value_by_day_offset(dated_dataset, 3)
        plus_4d = self.get_series_value_by_day_offset(dated_dataset, 4)
        plus_5d = self.get_series_value_by_day_offset(dated_dataset, 5)
        plus_6d = self.get_series_value_by_day_offset(dated_dataset, 6)
        plus_7d = self.get_series_value_by_day_offset(dated_dataset, 7)
        plus_8_to_14d = self.get_series_value_by_day_offset_range(dated_dataset, 8, 14)
        plus_15d_and_more = self.get_series_value_by_day_offset_range(dated_dataset, 15, -1)
        total = sum(dated_dataset)

        return [
            dated,
            plus_1d,
            plus_2d,
            plus_3d,
            plus_4d,
            plus_5d,
            plus_6d,
            plus_7d,
            plus_8_to_14d,
            plus_15d_and_more,
            total
        ]

    def get_series_value_by_day_offset(self, series, day):
        index = day - 1
        if len(series) >= day:
            return series[index]
        else:
            return None

    def get_series_value_by_day_offset_range(self, series, start, end):
        index = start - 1
        if len(series) >= start:
            subset = series[index:end]
            return sum(subset)
        else:
            return None

    def extract_total_tests_time_series_for_date(self, dated):
        """Extract all total tests values ranging from dated to last daily extract.
        """
        series = []
        num_days = (self.yesterday - dated).days

        for n in range(num_days):
            # Remember offset since tests are reported next day
            next_day = n + 1
            extract_date = dated + timedelta(next_day)
            extract = self.daily_extracts[extract_date]
            total_tests = extract.admin_tests.get(dated)
            series.append(int(total_tests))

        return series

    def extract_new_tests_time_series_for_date(self, dated):
        series = []
        total_tests_series = self.total_tests_time_series.get(dated)

        for n, total_tests in enumerate(total_tests_series):
            if n == 0:
                series.append(total_tests)
                continue

            prev = total_tests_series[n-1]
            new_tests = total_tests - prev
            series.append(int(new_tests))

        return series

    def extract_total_positives_time_series_for_date(self, dated):
        series = []
        num_days = (self.yesterday - dated).days

        for n in range(num_days):
            # Remember offset since tests are reported next day
            next_day = n + 1
            extract_date = dated + timedelta(next_day)
            extract = self.daily_extracts[extract_date]
            total_tests = extract.positive_tests.get(dated)
            series.append(int(total_tests))

        return series

    def extract_new_positives_time_series_for_date(self, dated):
        series = []
        totals_series = self.total_positives_time_series.get(dated)

        for n, totals in enumerate(totals_series):
            if n == 0:
                series.append(totals)
                continue

            prev = totals_series[n-1]
            new_positives = totals - prev
            series.append(int(new_positives))

        return series

"""
OC Daily Testing Export

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
#
# Imports
#
from os import listdir
from os.path import join as path_join, isfile
from functools import cached_property
import csv
from datetime import date, datetime, timedelta

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_archive_extract import OcDailyArchiveExtract


#
# Constants
#
OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-hca-testing.csv'

# First date I started archiving spec data.
START_DATE = '2020-08-03'

CSV_HEADER = [
    'Date',

    # Delays
    'Avg Test Delay (Days)',
    'Effective Admin Date',
    'Oldest Test Reported',

    # Test Counts
    'Tests Reported (Repo)',
    'Test Specs Repo',
    'Test Specs Admin',

    # Positive Counts
    'Pos Specs Repo',
    'New Cases Repo',
    'Pos Specs Admin',

    # Averages
    '7d Avg Test Delay',
    '7d Avg Test Specs',
    '7d Avg Pos Specs',
    '7d Avg Spec Pos Rate',
    '7d Avg Case Rate',

    # Delay Distributions
    'Tests Delayed 1-2d',
    '3-4d',
    '5-7d',
    '8-14d',
    '15+d',

    'Pos Tests Delayed 1-2d',
    '3-4d',
    '5-7d',
    '8-14d',
    '15+d'
]


#
# Export Class
#
class OcDailyTestsExport:
    #
    # Properties
    #
    # Dates
    @cached_property
    def start_date(self):
        return datetime.strptime(START_DATE, '%Y-%m-%d').date()

    @cached_property
    def end_date(self):
        return max(self.extract_dates)

    @cached_property
    def extract_dates(self):
        extract_dates = []
        archive_path = path_join(OC_DATA_PATH, 'daily')

        for fname in listdir(archive_path):
            extract_path = path_join(archive_path, fname)

            if isfile(extract_path):
                yyyymmdd = ''.join(c for c in fname if c.isdigit())
                extract_date = datetime.strptime(yyyymmdd, '%Y%m%d').date()
                extract_dates.append(extract_date)

        return extract_dates

    @property
    def yesterday(self):
        return date.today() - timedelta(days=1)

    @cached_property
    def dates(self):
        dates = []
        of_days = (self.end_date - self.start_date).days + 1

        for n in range(of_days):
            dated = self.start_date + timedelta(days=n)
            dates.append(dated)

        return dates

    # File Info
    @cached_property
    def csv_path(self):
        return path_join(OC_DATA_PATH, EXPORT_FILE_NAME)

    # Extracts
    @cached_property
    def daily_extracts(self):
        dated_extracts = {}

        for extract_date in self.dates:
            extract = OcDailyArchiveExtract(extract_date)
            dated_extracts[extract_date] = extract

        return dated_extracts

    @cached_property
    def most_recent_daily_extract(self):
        return self.daily_extracts[self.end_date]

    # Time Series
    @cached_property
    def total_tests_time_series(self):
        # Note: The extract for a given date will only report tests through the previous day.
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

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    def to_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                writer.writerow(self.extract_data_to_csv_row(dated))

        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, extract_date):
        extract = self.daily_extracts[extract_date]
        latest_extract = self.most_recent_daily_extract

        # Remember: the extract will be reporting values from the day previous.
        reporting_date = extract_date - timedelta(days=1)

        # Test Series
        tests_series = self.new_tests_time_series.get(reporting_date, [])
        pos_series = self.new_positives_time_series.get(reporting_date, [])

        # Delays
        daily_avg_delay = self.average_delay_for_series(tests_series)
        effective_reporting_date = reporting_date - timedelta(days=daily_avg_delay)
        avg_test_delay_7d = self.average_7d_test_delay_for_date(reporting_date)

        # Distributions
        tests_delayed_1_to_2d = self.get_series_value_by_day_offset_range(tests_series, 1, 2)
        tests_delayed_3_to_4d = self.get_series_value_by_day_offset_range(tests_series, 3, 4)
        tests_delayed_5_to_7d = self.get_series_value_by_day_offset_range(tests_series, 5, 6)
        tests_delayed_8_to_14d = self.get_series_value_by_day_offset_range(tests_series, 8, 14)
        tests_delayed_15d_plus = self.get_series_value_by_day_offset_range(tests_series, 15, -1)

        pos_delayed_1_to_2d = self.get_series_value_by_day_offset_range(pos_series, 1, 2)
        pos_delayed_3_to_4d = self.get_series_value_by_day_offset_range(pos_series, 3, 4)
        pos_delayed_5_to_7d = self.get_series_value_by_day_offset_range(pos_series, 5, 6)
        pos_delayed_8_to_14d = self.get_series_value_by_day_offset_range(pos_series, 8, 14)
        pos_delayed_15d_plus = self.get_series_value_by_day_offset_range(pos_series, 15, -1)

        return [
            reporting_date,

            # Delays
            daily_avg_delay,
            effective_reporting_date,
            extract.oldest_updated_admin_test,

            # Test Counts
            extract.reported_new_tests,
            extract.reported_total_admin_tests,
            self.most_recent_daily_extract.admin_tests.get(reporting_date, 'N/A'),

            # Positive Counts
            extract.reported_total_positive_tests,
            extract.reported_new_cases_for_yesterday,
            latest_extract.positive_tests.get(reporting_date, 'N/A'),

            # Averages
            avg_test_delay_7d,
            latest_extract.dated_7d_avg_test_specs.get(reporting_date, 'N/A'),
            latest_extract.dated_7d_avg_positive_specs.get(reporting_date, 'N/A'),
            latest_extract.dated_7d_avg_spec_positive_rate.get(reporting_date, 'N/A'),
            latest_extract.dated_7d_avg_positive_case_rate.get(reporting_date, 'N/A'),

            # Delay Distributions for Tests
            tests_delayed_1_to_2d,
            tests_delayed_3_to_4d,
            tests_delayed_5_to_7d,
            tests_delayed_8_to_14d,
            tests_delayed_15d_plus,

            # Delay Distributions for Positive Tests
            pos_delayed_1_to_2d,
            pos_delayed_3_to_4d,
            pos_delayed_5_to_7d,
            pos_delayed_8_to_14d,
            pos_delayed_15d_plus
        ]

    def average_delay_for_series(self, series):
        tests = []
        test_delay_days = []

        for n, count in enumerate(series):
            delay = n + 1
            if count > 0:
                tests.append(count)
                test_delay_days.append(count * delay)

        if sum(tests) < 1:
            return 0

        return sum(test_delay_days) / sum(tests)

    def average_7d_test_delay_for_date(self, reporting_date):
        tests = []
        test_delay_days = []

        for n in range(7):
            dated = reporting_date - timedelta(days=n)
            tests_series = self.new_tests_time_series.get(dated)

            if not tests_series:
                return None

            for n, count in enumerate(tests_series):
                delay = n + 1
                if count > 0:
                    tests.append(count)
                    test_delay_days.append(count * delay)

        return sum(test_delay_days) / sum(tests)

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
        num_days = (self.end_date - dated).days

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
        num_days = (self.end_date - dated).days

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

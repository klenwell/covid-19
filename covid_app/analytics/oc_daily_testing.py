"""
OC Daily Testing Analysis

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import date, timedelta
from calendar import monthrange, month_name

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_archive_extract import OcDailyArchiveExtract


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE_NAME_F = 'oc-daily-test-analysis-{}.csv'

CSV_HEADER = [
    'Date',
    'Daily Test Repo',
    'Daily New Cases',
    'Repo Case Pos Rate',
    'Daily Total Spec',
    'Daily Pos Spec',
    'Spec Test Pos Rate',
    'Avg Spec Delay',       # Days
    'Spec Delay Std Dev',   # Days
    'Oldest Spec Updated'
]


class OcDailyTestingAnalysis:
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

        for extract_date in self.dates:
            extract = OcDailyArchiveExtract(extract_date)
            dated_extracts[extract_date] = extract

        return dated_extracts

    @property
    def days_in_month(self):
        # https://stackoverflow.com/a/4938459/1093087
        return monthrange(self.year, self.month)[-1]

    @property
    def yesterday(self):
        return date.today() - timedelta(days=1)

    @property
    def month_name(self):
        return month_name[self.month]

    #
    # Instance Method
    #
    def __init__(self, year, month):
        self.year = year
        self.month = month

    def to_csv(self):
        year_month = '{}{:02}'.format(self.year, self.month)
        file_name = ANALYTICS_FILE_NAME_F.format(year_month)
        csv_path = path_join(OC_ANALYTICS_DATA_PATH, file_name)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                writer.writerow(self.extract_data_to_csv_row(dated))

        return csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        extract = self.daily_extracts[dated]
        return [
            dated,
            extract.reported_new_tests,
            extract.reported_new_cases_for_yesterday,
            extract.reported_case_positive_rate,
            extract.reported_total_admin_tests,
            extract.reported_total_positive_tests,
            extract.reported_test_positive_rate,
            extract.average_test_delay,
            extract.test_delay_stdev,
            extract.oldest_updated_admin_test
        ]

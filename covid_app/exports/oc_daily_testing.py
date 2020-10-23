"""
OC Daily Testing Export

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import date, datetime, timedelta

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_archive_extract import OcDailyArchiveExtract


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-hca-testing.csv'

START_DATE = '2020-08-03'

CSV_HEADER = [
    'Date',
    '7d Avg Test Delay (Days)',
    'Effective Reporting Date',
    'Tests Reported (Repo)',
    'Test Specs Reported',
    'Pos Specs Reported',
    'New Cases Reported',
    'Test Specs Dated Today',
    'Pos Specs Dated Today',
    'Oldest Test Reported',
    '7d Avg Test Specs',
    '7d Avg Pos Specs',
    '7d Avg Spec Pos Rate',
    '7d Avg Case Rate',
    'Tests Delayed 1-2d',
    'Tests Delayed 3-4d',
    'Tests Delayed 5-7d',
    'Tests Delayed 8-14d',
    'Tests Delayed 15+d',
    'Pos Tests Delayed 1-2d',
    'Pos Tests Delayed 3-4d',
    'Pos Tests Delayed 5-7d',
    'Pos Tests Delayed 8-14d',
    'Pos Tests Delayed 15+d'
]


class OcDailyTestsExport:
    #
    # Properties
    #
    @cached_property
    def start_date(self):
        return datetime.strptime(START_DATE, '%Y-%m-%d').date()

    @cached_property
    def end_date(self):
        return self.yesterday

    @cached_property
    def dates(self):
        dates = []
        of_days = (self.end_date - self.start_date).days + 1

        for n in range(of_days):
            dated = self.start_date + timedelta(days=n)
            dates.append(dated)

        return dates

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

    @cached_property
    def csv_path(self):
        return path_join(OC_DATA_PATH, EXPORT_FILE_NAME)

    @property
    def yesterday(self):
        return date.today() - timedelta(days=1)

    #
    # Instance Method
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

        # Remember: the extract will be reporting values from the day previous.
        reporting_date = extract_date - timedelta(days=1)

        return [
            reporting_date,
            '7d Avg Test Delay (Days)',
            'Effective Reporting Date',
            extract.reported_new_tests,
            extract.reported_total_admin_tests,
            extract.reported_total_positive_tests,
            extract.reported_new_cases_for_yesterday,
            self.most_recent_daily_extract.admin_tests.get(reporting_date, 'N/A'),
            self.most_recent_daily_extract.positive_tests.get(reporting_date, 'N/A'),
            extract.oldest_updated_admin_test,
            '7d Avg Test Specs',
            '7d Avg Pos Specs',
            '7d Avg Spec Pos Rate',
            '7d Avg Case Rate',
            'Tests Delayed 1-2d',
            'Tests Delayed 3-4d',
            'Tests Delayed 5-7d',
            'Tests Delayed 8-14d',
            'Tests Delayed 15+d',
            'Pos Tests Delayed 1-2d',
            'Pos Tests Delayed 3-4d',
            'Pos Tests Delayed 5-7d',
            'Pos Tests Delayed 8-14d',
            'Pos Tests Delayed 15+d'
        ]

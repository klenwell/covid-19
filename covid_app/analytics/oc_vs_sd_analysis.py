"""
OC vs SD Analysis

Compare key COVID-19 metric for Orange and San Diego counties.
"""
#
# Imports
#
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import timedelta, date

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import (DailyCovid19Extract as OcExtract,
                                                             OC_POPULATION)
from covid_app.extracts.san_diego_county import (SanDiegoCountyDailyExtract as SdExtract,
                                                 TOTAL_POPULATION as SD_POPULATION)


#
# Constants
#
OC_ANALYTICS_PATH = path_join(DATA_ROOT, 'oc', 'analytics')
EXPORT_FILE_NAME = 'oc-vs-sd.csv'

CSV_HEADER = [
    'Date',

    # Per 100k Columns
    'OC Tests per 100k',
    'SD Tests per 100k',
    'OC Cases per 100k',
    'SD Cases per 100k',

    '(Blank)',

    # 7-Day Averages / Diffs
    'SD Tests 7d',
    'OC Tests 7d',
    'SD/OC Tests Diff',

    '(Blank)',

    'SD Cases 7d',
    'OC Cases 7d',
    'SD/OC Cases Diff',

    '(Blank)',

    'SD Case Pos Rate 7d',
    'OC Case Pos Rate 7d',
    'SD/OC Case Pos Diff'
]


#
# Export Class
#
class OrangeCoVsSanDiegoAnalysis:
    #
    # Properties
    #
    # Extracts
    @cached_property
    def oc_extract(self):
        return OcExtract.latest()

    @cached_property
    def sd_extract(self):
        return SdExtract()

    # Dates
    @cached_property
    def starts_on(self):
        return date(2020, 4, 1)

    @cached_property
    def ends_on(self):
        return min(self.sd_extract.ends_on, self.oc_extract.ends_on)

    @cached_property
    def dates(self):
        dates = []
        of_days = (self.ends_on - self.starts_on).days + 1

        for n in range(of_days):
            dated = self.starts_on + timedelta(days=n)
            dates.append(dated)

        return dates

    # File Info
    @property
    def csv_path(self):
        return path_join(OC_ANALYTICS_PATH, EXPORT_FILE_NAME)

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
    def extract_data_to_csv_row(self, dated):
        def format_1f(value):
            return '{0:.1f}'.format(value)

        oc_tests = self.oc_extract.new_tests_reported.get(dated)
        sd_tests = self.sd_extract.new_tests_reported.get(dated)
        oc_tests_per_100k = oc_tests / OC_POPULATION * 100000
        sd_tests_per_100k = sd_tests / SD_POPULATION * 100000

        oc_cases = self.oc_extract.new_cases.get(dated)
        sd_cases = self.sd_extract.new_cases.get(dated)
        oc_cases_per_100k = oc_cases / OC_POPULATION * 100000
        sd_cases_per_100k = sd_cases / SD_POPULATION * 100000

        return [
            dated,

            # Per 100k Columns
            format_1f(oc_tests_per_100k),
            format_1f(sd_tests_per_100k),
            format_1f(oc_cases_per_100k),
            format_1f(sd_cases_per_100k),

            '',

            # 7-Day Averages / Diffs
            'SD Tests 7d',
            'OC Tests 7d',
            'SD/OC Tests Diff',

            '',

            'SD Cases 7d',
            'OC Cases 7d',
            'SD/OC Cases Diff',

            '',

            'SD Case Pos Rate 7d',
            'OC Case Pos Rate 7d',
            'SD/OC Case Pos Diff'
        ]

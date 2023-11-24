"""
OcInfectionsExport

The export is meant to be run nightly. It provides a daily snapshot of Covid data focused on
infections and the infection rate. The data primarily comes from the OC Health Care Agency
and CA Dept of Public Health.

By default, it will save export file to data/oc/daily/oc-hca-<YYYYMMDD>.csv.

For more information, see:
https://occovid19.ochealthinfo.com/coronavirus-in-oc
"""
from os.path import join as path_join
from functools import cached_property
from datetime import datetime
import csv
import time

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_extract import OcHcaDailyExtract
from covid_app.extracts.cdph.oc_hospitalization_extract import OcHospitalDataExtract


#
# Constants
#
OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ARCHIVE_PATH = path_join(OC_DATA_PATH, 'daily')


class OcInfectionsExport:
    def __init__(self, test=False):
        self.run_time_start = time.time()
        self.run_time_end = None
        self.test = test

    #
    # Properties
    #
    @cached_property
    def extract(self):
        return OcHcaDailyExtract()

    @cached_property
    def hospital_extract(self):
        return OcHospitalDataExtract()

    @property
    def csv_path(self):
        file_f = 'oc-hca-{}.csv'
        file_name = file_f.format(datetime.now().strftime('%Y%m%d'))
        return path_join(OC_ARCHIVE_PATH, file_name)

    @cached_property
    def csv_headers(self):
        return [
            'Date',
            'New Tests Administered',
            'Pos Tests Administered',
            'New Tests Reported',
            'New Cases',
            'Hospitalizations',
            'ICU',
            'New Deaths',
            'SNF Cases'
        ]

    @cached_property
    def dates(self):
        return self.extract.dates

    @property
    def run_time(self):
        if not self.run_time_end:
            self.run_time_end = time.time()

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def to_csv_file(self, csv_path=None):
        if not csv_path:
            csv_path = self.csv_path

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.csv_headers)

            for dated in reversed(self.dates):
                writer.writerow(self.csv_row_by_date(dated))

        return csv_path

    #
    # Private
    #
    def csv_row_by_date(self, dated):
        return [
            dated,
            self.extract.new_tests_administered.get(dated),
            self.extract.new_positive_tests_administered.get(dated),
            self.extract.new_tests_reported.get(dated),
            self.extract.new_cases.get(dated),
            self.hospital_extract.hospitalizations.get(dated),
            self.hospital_extract.icu_cases.get(dated),
            self.extract.new_deaths.get(dated),
            self.extract.new_snf_cases.get(dated)
        ]

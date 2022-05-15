from os.path import join as path_join
import csv
from functools import cached_property
import time

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract


#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-hca.csv'

CSV_HEADER = [
    'Date',
    'Tests Admin',
    'Pos Tests Admin',
    'Tests Reported',
    'Cases Reported',
    'Hospital',
    'ICU',
    'Deaths'
]


class OcDailyDataExport:
    #
    # Properties
    #
    @property
    def csv_path(self):
        return path_join(CSV_DATA_PATH, EXPORT_FILE_NAME)

    @cached_property
    def oc_hca_extract(self):
        return DailyCovid19Extract.latest()

    @property
    def dates(self):
        return sorted(self.oc_hca_extract.dates)

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    @property
    def run_time(self):
        if not self.run_time_end:
            return None

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self):
        self.run_time_start = time.time()

    def to_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                writer.writerow(self.extract_data_to_csv_row(dated))

        self.run_time_end = time.time()
        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        return [
            dated,
            self.oc_hca_extract.new_tests_administered.get(dated),
            self.oc_hca_extract.new_positive_tests_administered.get(dated),
            self.oc_hca_extract.new_tests_reported.get(dated),
            self.oc_hca_extract.new_cases.get(dated),
            self.oc_hca_extract.hospitalizations.get(dated),
            self.oc_hca_extract.icu_cases.get(dated),
            self.oc_hca_extract.new_deaths.get(dated),
        ]

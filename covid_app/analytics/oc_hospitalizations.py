"""
OC Hospitalizations Analysis

For info on OC HCA tests data source, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE = 'oc-hospitalizations-daily.csv'
CSV_COLUMNS = ['Date',
               'Reported New Tests',
               'Administered New Tests',
               'Administered Postive Tests',
               'Test Positive Rate',
               'New Cases',
               'Projected Cases at 10k Tests',
               'Hospitalizations',
               'ICU Cases',
               'New Deaths']


class OcHospitalizationsAnalysis:
    #
    # Static Methods
    #
    @staticmethod
    def predict_by_positive_rate():
        pass

    #
    # Properties
    #
    @cached_property
    def extract(self):
        return DailyCovid19ExtractV3()

    @cached_property
    def daily_test_logs(self):
        return self.extract.daily_test_logs

    @cached_property
    def daily_case_logs(self):
        return self.extract.daily_case_logs

    @cached_property
    def total_positive_specimens(self):
        return self.daily_test_logs[-1]['tot_pcr_pos']

    @cached_property
    def total_cases(self):
        return self.daily_case_logs[-1]['total_cases_repo']

    @cached_property
    def dates(self):
        administered_dates = set(self.extract.new_tests_administered.keys())
        reported_dates = set(self.extract.new_tests_reported.keys())
        return sorted(list(administered_dates | reported_dates))

    #
    # Instance Method
    #
    def __init__(self):
        pass

    def to_csv(self):
        csv_path = path_join(OC_ANALYTICS_DATA_PATH, ANALYTICS_FILE)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)

            for dated in reversed(self.dates):
                writer.writerow(self.data_to_csv_row(dated))

        return csv_path

    def data_to_csv_row(self, dated):
        tests_reported = self.extract.new_tests_reported.get(dated)
        tests_administered = self.extract.new_tests_administered.get(dated)
        pos_tests_administered = self.extract.new_positive_tests_administered.get(dated)
        pos_rate = self.compute_positive_rate(tests_administered, pos_tests_administered)
        new_cases = self.extract.new_cases.get(dated)
        projected_cases = self.project_cases_by_case_rate(10000, tests_administered,
                                                          pos_tests_administered)
        hospitalizations = self.extract.hospitalizations.get(dated)
        icu_cases = self.extract.icu_cases.get(dated)
        new_deaths = self.extract.new_deaths.get(dated)

        return [
            dated,
            tests_reported,
            tests_administered,
            pos_tests_administered,
            pos_rate,
            new_cases,
            projected_cases,
            hospitalizations,
            icu_cases,
            new_deaths
        ]

    def compute_positive_rate(self, tests_administered, pos_tests_administered):
        if pos_tests_administered is None:
            return None

        if not tests_administered:
            return None

        return pos_tests_administered / tests_administered

    def project_cases_by_case_rate(self, target, tests_administered, pos_tests_administered):
        positive_rate = self.compute_positive_rate(tests_administered, pos_tests_administered)

        if positive_rate is None:
            return None

        return positive_rate * target

"""
OC Hospitalizations Analysis

For info on OC HCA tests data source, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import timedelta

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE = 'oc-hospitalizations-daily.csv'
CSV_COLUMNS = ['Date',
               'Administered New Tests',
               'Administered Postive Tests',
               'Test Positive Rate',
               '7-Day Test Positive Rate',
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
        tests_administered = self.extract.new_tests_administered.get(dated)
        pos_tests_administered = self.extract.new_positive_tests_administered.get(dated)
        pos_rate = self.compute_positive_rate_for_date(dated)
        pos_rate_7d = self.compute_7d_positive_rate_for_date(dated)
        new_cases = self.extract.new_cases.get(dated)
        projected_cases = self.project_cases_by_case_rate_for_date(10000, dated)
        hospitalizations = self.extract.hospitalizations.get(dated)
        icu_cases = self.extract.icu_cases.get(dated)
        new_deaths = self.extract.new_deaths.get(dated)

        return [
            dated,
            tests_administered,
            pos_tests_administered,
            pos_rate,
            pos_rate_7d,
            new_cases,
            projected_cases,
            hospitalizations,
            icu_cases,
            new_deaths
        ]

    def compute_positive_rate_for_date(self, dated):
        tests_administered = self.extract.new_tests_administered.get(dated)
        pos_tests_administered = self.extract.new_positive_tests_administered.get(dated)

        if pos_tests_administered is None:
            return None

        if not tests_administered:
            return None

        return pos_tests_administered / tests_administered

    def compute_7d_positive_rate_for_date(self, dated):
        test_counts = []
        positive_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            tests_administered = self.extract.new_tests_administered.get(on_date)
            pos_tests_administered = self.extract.new_positive_tests_administered.get(on_date)

            if tests_administered is None or pos_tests_administered is None:
                return None

            test_counts.append(tests_administered)
            positive_counts.append(pos_tests_administered)

        return sum(positive_counts) / sum(test_counts)

    def project_cases_by_case_rate_for_date(self, project_targeted, dated):
        positive_rate = self.compute_7d_positive_rate_for_date(dated)

        if positive_rate is None:
            return None

        return positive_rate * project_targeted

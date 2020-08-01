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
ANALYTICS_FILE = 'oc-tests-reporting.csv'
CSV_COLUMNS = ['Date', 'Administered', 'Reported', 'Avg Days Wait', 'Wait Std Dev',
               'Wait Min', 'Wait Max']


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
    def administered_tests_by_date(self):
        pass

    @cached_property
    def reported_tests_by_date(self):
        pass

    @cached_property
    def dates(self):
        administered_dates = set(self.administered_tests_by_date.keys())
        reported_dates = set(self.reported_tests_by_date.keys())
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
        tests_administered = self.administered_tests_by_date.get(dated)
        tests_reported = self.reported_tests_by_date.get(dated)

        return [
            dated,
            tests_administered,
            tests_reported
        ]

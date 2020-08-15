"""
OC Hospitalizations Analysis

For info on OC HCA tests data source, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import timedelta
from collections import deque

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE = 'oc-hospitalizations-daily.csv'
CSV_COLUMNS = ['Date',
               'Hospitalizations',
               'New SNF Cases',
               'Estimated SNF Cases at 10d per Case',
               'Estimated SNF Cases at 30d per Case',
               '7-Day Hospitalization Avg',
               '7-Day New SNF Cases Avg',
               '7-Day 10d SNF Avg',
               '7-Day Total Hospital Avg',
               '7-Day Test Positive Rate']


class OcHospitalizationsAnalysis:
    #
    # Properties
    #
    @cached_property
    def extract(self):
        return DailyCovid19ExtractV3()

    @cached_property
    def new_snf_cases(self):
        daily_snf_cases = {}

        for dated in self.dates:
            day_before = dated - timedelta(days=1)

            snf_cases_today = self.extract.total_snf_cases.get(dated)
            snf_cases_yesterday = self.extract.total_snf_cases.get(day_before)

            if snf_cases_today is None:
                continue

            if snf_cases_yesterday is None:
                snf_cases_yesterday = 0

            new_cases = snf_cases_today - snf_cases_yesterday
            daily_snf_cases[dated] = new_cases

        return daily_snf_cases

    @cached_property
    def estimated_snf_cases_when_10d_long(self):
        return self.estimate_active_snf_cases_by_duration(10)

    @cached_property
    def estimated_snf_cases_when_30d_long(self):
        return self.estimate_active_snf_cases_by_duration(30)

    @cached_property
    def dates(self):
        hospitalization_dates = set(self.extract.hospitalizations.keys())
        return sorted(hospitalization_dates)

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
        hospitalizations = self.extract.hospitalizations.get(dated)
        snf_cases = self.new_snf_cases.get(dated)
        estimated_snf_cases_10d = self.estimated_snf_cases_when_10d_long.get(dated)
        estimated_snf_cases_30d = self.estimated_snf_cases_when_30d_long.get(dated)
        hospital_avg_7d = self.compute_7d_hospital_avg_for_date(dated)
        new_snf_avg_7d = self.compute_7d_new_snf_avg_for_date(dated)
        snf_10d_avg_7d = self.compute_7d_snf_10d_avg_for_date(dated)
        total_hospital_avg_7d = hospital_avg_7d + snf_10d_avg_7d if \
            (hospital_avg_7d and snf_10d_avg_7d) else None
        pos_rate_7d = self.compute_7d_positive_rate_for_date(dated)

        return [
            dated,
            hospitalizations,
            snf_cases,
            estimated_snf_cases_10d,
            estimated_snf_cases_30d,
            hospital_avg_7d,
            new_snf_avg_7d,
            snf_10d_avg_7d,
            total_hospital_avg_7d,
            pos_rate_7d
        ]

    def estimate_active_snf_cases_by_duration(self, duration):
        active_snf_cases = {}
        snf_queue = deque([0] * duration)

        for dated in self.dates:
            new_snf_cases = self.new_snf_cases.get(dated, 0)
            snf_queue.pop()
            snf_queue.appendleft(new_snf_cases)
            active_snf_cases[dated] = sum(snf_queue)

        return active_snf_cases

    def compute_7d_hospital_avg_for_date(self, dated):
        case_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            cases = self.extract.hospitalizations.get(on_date)

            if cases is None:
                return None

            case_counts.append(cases)

        return sum(case_counts) / len(case_counts)

    def compute_7d_new_snf_avg_for_date(self, dated):
        case_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            cases = self.new_snf_cases.get(on_date)

            if cases is None:
                return None

            case_counts.append(cases)

        return sum(case_counts) / len(case_counts)

    def compute_7d_snf_10d_avg_for_date(self, dated):
        case_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            cases = self.estimated_snf_cases_when_10d_long.get(on_date)

            if cases is None:
                return None

            case_counts.append(cases)

        return sum(case_counts) / len(case_counts)

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

        if not sum(test_counts):
            return None

        return sum(positive_counts) / sum(test_counts)

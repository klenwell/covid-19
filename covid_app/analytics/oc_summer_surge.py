"""
OC Summer Surge Analysis

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import datetime, timedelta

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3
from covid_app.extracts.unacast_social_distancing import UnacastSocialDistancingExtract


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE = 'oc-summer-surge.csv'

CSV_COLUMNS = ['Date',
               '7d Positive Rate',
               '7d Wander Rate',
               '7d Density',
               '7d Tests',
               '7d Positive Tests',
               'Daily Positive Rate',
               'Hospital Cases',
               'ICU Cases',
               'Annotations',
               '(Blank)',
               'New Tests',
               'Positive Tests',
               'New Deaths']

ANNOTATIONS = (
    ('2020-05-18', 'CA eases reopening rules'),
    ('2020-05-26', 'OC enters Phase 3'),
    ('2020-06-06', 'OC HCA chief resigns'),
    ('2020-06-18', 'CA mandates masks'),
    ('2020-07-01', 'CA/OC roll back opening')
)


class OcSummerSurgeAnalysis:
    #
    # Properties
    #
    @cached_property
    def extract(self):
        return DailyCovid19ExtractV3()

    @cached_property
    def unacast_extract(self):
        return UnacastSocialDistancingExtract.oc()

    @cached_property
    def annotations(self):
        dated_annotations = {}

        for yyyy_mm_dd, annotation in ANNOTATIONS:
            dated = datetime.strptime(yyyy_mm_dd, '%Y-%m-%d').date()
            dated_annotations[dated] = annotation

        return dated_annotations

    @cached_property
    def estimated_snf_cases_when_10d_long(self):
        return self.estimate_active_snf_cases_by_duration(10)

    @cached_property
    def estimated_snf_cases_when_30d_long(self):
        return self.estimate_active_snf_cases_by_duration(30)

    @cached_property
    def dates(self):
        hospitalization_dates = set(self.extract.new_tests_administered.keys())
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
        pos_rate_7d = self.compute_7d_positive_rate_for_date(dated)
        wander_rate_7d = self.compute_7d_wander_rate_for_date(dated)
        density_7d = self.compute_7d_encounter_density_for_date(dated)
        tests_7d = self.compute_7d_tests_avg_for_date(dated)
        pos_tests_7d = self.compute_7d_positive_tests_avg_for_date(dated)
        daily_pos_rate = self.compute_daily_positive_rate_for_date(dated)
        hospital_7d = self.compute_7d_hospital_avg_for_date(dated)
        icu_7d = self.compute_7d_icu_avg_for_date(dated)
        annotation = self.annotations.get(dated)
        blank = '-'
        new_tests = self.extract.new_tests_administered.get(dated)
        pos_tests = self.extract.new_positive_tests_administered.get(dated)
        new_deaths = self.extract.new_deaths.get(dated)

        return [
            dated,
            pos_rate_7d,
            wander_rate_7d,
            density_7d,
            tests_7d,
            pos_tests_7d,
            daily_pos_rate,
            hospital_7d,
            icu_7d,
            annotation,
            blank,
            new_tests,
            pos_tests,
            new_deaths
        ]

    #
    # Private
    #
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

    def compute_daily_positive_rate_for_date(self, dated):
        tests_administered = self.extract.new_tests_administered.get(dated)
        pos_tests_administered = self.extract.new_positive_tests_administered.get(dated)

        if not tests_administered:
            return None

        if pos_tests_administered is None:
            pos_tests_administered = 0

        return pos_tests_administered / tests_administered

    def compute_7d_wander_rate_for_date(self, dated):
        values = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)

            # Minimum (ideal) would -100 for each of these, meaning people fully locked down.
            travel_score = self.unacast_extract.travel_distance_scores.get(on_date)
            visitation_score = self.unacast_extract.visitation_scores.get(on_date)

            if travel_score is None or visitation_score is None:
                return None

            distancing_score = 100 + ((travel_score + visitation_score) * 100 / 2)
            values.append(distancing_score)

        return sum(values) / len(values)

    def compute_7d_encounter_density_for_date(self, dated):
        values = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            value = self.unacast_extract.encounter_densities.get(on_date)

            if value is None:
                return None

            values.append(value)

        return sum(values) / len(values)

    def compute_7d_tests_avg_for_date(self, dated):
        test_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            tests_administered = self.extract.new_tests_administered.get(on_date)

            if tests_administered is None:
                return None

            test_counts.append(tests_administered)

        return sum(test_counts) / len(test_counts)

    def compute_7d_positive_tests_avg_for_date(self, dated):
        positive_test_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            positive_tests = self.extract.new_positive_tests_administered.get(on_date)

            if positive_tests is None:
                return None

            positive_test_counts.append(positive_tests)

        return sum(positive_test_counts) / len(positive_test_counts)

    def compute_7d_hospital_avg_for_date(self, dated):
        case_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            cases = self.extract.hospitalizations.get(on_date)

            if cases is None:
                return None

            case_counts.append(cases)

        return sum(case_counts) / len(case_counts)

    def compute_7d_icu_avg_for_date(self, dated):
        case_counts = []

        for days_ago in range(7):
            on_date = dated - timedelta(days=days_ago)
            cases = self.extract.icu_cases.get(on_date)

            if cases is None:
                return None

            case_counts.append(cases)

        return sum(case_counts) / len(case_counts)

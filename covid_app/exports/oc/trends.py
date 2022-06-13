from os.path import join as path_join
from functools import cached_property
from datetime import timedelta
import time
import json

from config.app import GH_PAGES_ROOT
from covid_app.extracts.local.oc.daily_hca import OcDailyHcaExtract
from covid_app.extracts.cdph.oc_wastewater_extract import OcWastewaterExtract

#
# Constants
#
JSON_DATA_PATH = path_join(GH_PAGES_ROOT, 'data', 'json', 'oc')
JSON_FILE_NAME = 'trends.json'

# Wastewater Lab: CAL3 or DWRL
WASTEWATER_LAB = 'DWRL'

JSON_SCHEMA = {
    'weeks': [],
    'meta': {}
}

DATE_OUT_F = '%Y-%m-%d'


class OcTrendsExport:
    #
    # Properties
    #
    @property
    def json_path(self):
        return path_join(JSON_DATA_PATH, JSON_FILE_NAME)

    # Extracts
    @cached_property
    def waste_extract(self):
        pass

    @cached_property
    def case_extract(self):
        return OcDailyHcaExtract()

    # Export Keys
    @cached_property
    def weeks(self):
        return []

    @property
    def meta(self):
        return {}

    # Latest Update Dates
    @cached_property
    def latest_test_update(self):
        for dated in self.case_dates:
            if self.admin_tests.get(dated) and self.positive_tests.get(dated):
                return dated

    @cached_property
    def latest_case_update(self):
        dataset = self.case_extract.new_cases
        for dated in self.case_dates:
            if dataset.get(dated):
                return dated

    @cached_property
    def latest_hospital_case_update(self):
        for dated in self.case_dates:
            if self.case_extract.hospitalizations.get(dated) not in ('', None):
                return dated

    @cached_property
    def latest_icu_case_update(self):
        for dated in self.case_dates:
            if self.case_extract.icu_cases.get(dated) not in ('', None):
                return dated

    @cached_property
    def latest_death_update(self):
        for dated in self.case_dates:
            if self.case_extract.new_deaths.get(dated) not in ('', None):
                return dated

    @cached_property
    def latest_wastewater_update(self):
        return self.waste_extract.latest_update_by_lab(WASTEWATER_LAB)

    # Date sets
    @property
    def case_dates(self):
        return sorted(self.case_extract.dates, reverse=True)

    # Dataset aliases
    @property
    def admin_tests(self):
        return self.case_extract.new_tests_administered

    @property
    def positive_tests(self):
        return self.case_extract.new_positive_tests_administered

    # Avgs datasets
    @cached_property
    def postive_rate_7d_avgs(self):
        daily_values = {}

        # Source: https://stackoverflow.com/a/993367/1093087
        start_from = self.latest_test_update
        max_length = len(self.admin_tests) - 14
        dates = [start_from - timedelta(days=n) for n in range(max_length)]

        for dated in dates:
            avg_tests_admin = self.week_avg_from_date(self.admin_tests, dated)
            avg_tests_pos = self.week_avg_from_date(self.positive_tests, dated)
            daily_values[dated] = avg_tests_pos / avg_tests_admin * 100.0

        return daily_values

    @cached_property
    def case_7d_avgs(self):
        daily_values = {}
        dataset = self.case_extract.new_cases
        start_from = self.latest_case_update
        max_length = len(dataset) - 14

        dates = [start_from - timedelta(days=n) for n in range(max_length)]

        for dated in dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def hospital_7d_avgs(self):
        daily_values = {}
        dataset = self.case_extract.hospitalizations
        start_from = self.latest_hospital_case_update
        max_length = len(dataset) - 14

        dates = [start_from - timedelta(days=n) for n in range(max_length)]

        for dated in dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def icu_7d_avgs(self):
        daily_values = {}
        dataset = self.case_extract.icu_cases
        start_from = self.latest_icu_case_update
        max_length = len(dataset) - 14

        dates = [start_from - timedelta(days=n) for n in range(max_length)]

        for dated in dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def death_7d_avgs(self):
        daily_values = {}
        dataset = self.case_extract.new_deaths
        start_from = self.latest_death_update
        max_length = len(dataset) - 14

        dates = [start_from - timedelta(days=n) for n in range(max_length)]

        for dated in dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    # Etc
    @property
    def run_time(self):
        if not self.run_time_end:
            self.run_time_end = time.time()

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self, test=False):
        self.run_time_start = time.time()
        self.run_time_end = None
        self.test = test

    def to_json_file(self):
        trends = JSON_SCHEMA.copy()

        trends['weeks'] = self.weeks
        trends['meta'] = self.meta

        # pretty print
        with open(self.json_path, 'w') as f:
            f.write(json.dumps(metrics, indent=4))

        return self.json_path

    #
    # Private
    #
    def compute_change(self, old, new):
        """Source: https://stackoverflow.com/q/30926840/1093087
        """
        return (new - old) / old * 100.0

    def week_avg_from_date(self, daily_values, from_date):
        values = []
        for n in range(7):
            dated = from_date - timedelta(days=n)
            value = daily_values[dated]
            values.append(value)
        return sum(values) / len(values)

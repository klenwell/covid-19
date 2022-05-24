from os.path import join as path_join
from functools import cached_property
from datetime import timedelta
import time
import json

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.extracts.cdph.oc_wastewater_extract import OcWastewaterExtract

#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'oc')
JSON_DATA_PATH = path_join(DATA_ROOT, 'api', 'oc')
JSON_FILE_NAME = 'metrics.json'

JSON_SCHEMA = {
    'testPositiveRate': {},
    'dailyNewCases': {},
    'wastewater': {},
    'hospitalCases': {},
    'icuCases': {},
    'deaths': {}
}


class OCMetricsExport:
    #
    # Properties
    #
    @property
    def json_path(self):
        return path_join(JSON_DATA_PATH, JSON_FILE_NAME)

    @cached_property
    def waste_extract(self):
        return OcWastewaterExtract()

    @cached_property
    def case_extract(self):
        return DailyCovid19Extract.latest()

    @cached_property
    def latest_test_update(self):
        pass

    @cached_property
    def latest_case_update(self):
        pass

    @cached_property
    def latest_wastewater_update(self):
        pass

    @cached_property
    def latest_hospital_case_update(self):
        pass

    @cached_property
    def latest_icu_case_update(self):
        pass

    @cached_property
    def latest_death_update(self):
        pass

    @property
    def admin_tests(self):
        return self.case_extract.new_tests_administered

    @property
    def positive_tests(self):
        return self.case_extract.new_positive_tests_administered

    @cached_property
    def postive_rate_7d_avg(self):
        daily_values = {}

        # Source: https://stackoverflow.com/a/993367/1093087
        start_from = self.latest_test_update
        max_length = 28
        dates = [start_from - timedelta(days=n+1) for n in range(max_length)]

        for dated in dates:
            avg_tests_admin = self.week_avg_from_date(self.admin_tests, dated)
            avg_tests_pos = self.week_avg_from_date(self.positive_tests, dated)
            daily_values[dated] = avg_tests_pos / avg_tests_admin

        return daily_values

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

    def to_json_file(self):
        metrics = JSON_SCHEMA.copy()

        metrics['testPositiveRate'] = self.prep_positive_rate_data()
        metrics['dailyNewCases'] = self.prep_daily_new_cases()
        metrics['wastewater'] = self.prep_wastewater()
        metrics['hospitalCases'] = self.prep_hospital_cases()
        metrics['icuCases'] = self.prep_icu_cases()
        metrics['deaths'] = self.prep_deaths()

        # pretty print
        with open(self.json_path, 'w') as f:
            f.write(json.dumps(metrics, indent=4))

        return self.json_path

    #
    # Private
    #
    def prep_positive_rate_data(self):
        updated_on = self.latest_test_update

        latest = self.postive_rate_7d_avg.get(updated_on)
        level = self.compute_level(latest, self.postive_rate_7d_avg.values())

        updated_on_d7 = updated_on - timedelta(days=7)
        value_d7 = self.postive_rate_7d_avg.get(updated_on_d7)
        delta_d7 = self.compute_change(value_d7, latest)

        updated_on_d14 = updated_on - timedelta(days=14)
        latest_d14 = self.postive_rate_7d_avg.get(updated_on_d14)
        delta_d14 = self.compute_change(latest_d14, latest)

        return {
            'updatedOn': updated_on,
            'latest': latest,
            'level': level,
            'd7Value': value_d7,
            'd7DeltaPct': delta_d7,
            'd14Value': latest_d14,
            'd14DeltaPct': delta_d14,
        }

    def compute_level(self, value, all_values):
        raise ValueError('Not Implemented')

    def week_avg_from_date(self, daily_values, from_date):
        values = []

        for n in range(7):
            dated = from_date - timedelta(days=n)
            value = daily_values[dated]
            values.append(value)

        return sum(values) / len(values)

    def prep_daily_new_cases(self):
        pass

    def prep_wastewater(self):
        pass

    def prep_hospital_cases(self):
        pass

    def prep_icu_cases(self):
        pass

    def prep_deaths(self):
        pass

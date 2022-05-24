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

DATE_OUT_F = '%Y-%m-%d'


class OCMetricsExport:
    #
    # Properties
    #
    @property
    def json_path(self):
        return path_join(JSON_DATA_PATH, JSON_FILE_NAME)

    # Extracts
    @cached_property
    def waste_extract(self):
        return OcWastewaterExtract()

    @cached_property
    def case_extract(self):
        return DailyCovid19Extract.latest()

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
    def latest_wastewater_update(self):
        return self.waste_extract.ends_on

    @cached_property
    def latest_hospital_case_update(self):
        for dated in self.case_dates:
            if self.hospitalizations.get(dated):
                return dated

    @cached_property
    def latest_icu_case_update(self):
        for dated in self.case_dates:
            if self.icu_cases.get(dated):
                return dated

    @cached_property
    def latest_death_update(self):
        for dated in self.case_dates:
            if self.new_deaths.get(dated):
                return dated

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
        max_length = 28
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
        max_length = 28

        dates = [start_from - timedelta(days=n) for n in range(max_length)]

        for dated in dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    # Etc
    @property
    def run_time(self):
        if not self.run_time_end:
            return None

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self, test=False):
        self.run_time_start = time.time()
        self.test = test

        if self.test:
            print('[WARNING] In test mode: loading sample data.')
            self.waste_extract.load_test_csv()
            self.case_extract.mock_api_calls()

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
        dataset = self.postive_rate_7d_avgs

        latest = dataset.get(updated_on)
        percentile = self.compute_percentile(latest, dataset.values())

        updated_on_d7 = updated_on - timedelta(days=7)
        value_d7 = dataset.get(updated_on_d7)
        delta_d7 = self.compute_change(value_d7, latest)

        updated_on_d14 = updated_on - timedelta(days=14)
        value_d14 = dataset.get(updated_on_d14)
        delta_d14 = self.compute_change(value_d14, latest)

        return {
            'updatedOn': updated_on.strftime(DATE_OUT_F),
            'latest': round(latest, 2),
            'percentile': round(percentile, 2),
            'd7Value': round(value_d7, 2),
            'd7DeltaPct': round(delta_d7, 2),
            'd14Value': round(value_d14, 2),
            'd14DeltaPct': round(delta_d14, 2),
        }

    def prep_daily_new_cases(self):
        updated_on = self.latest_case_update
        dataset = self.case_7d_avgs

        latest = dataset.get(updated_on)
        percentile = self.compute_percentile(latest, dataset.values())

        updated_on_d7 = updated_on - timedelta(days=7)
        value_d7 = dataset.get(updated_on_d7)
        delta_d7 = self.compute_change(value_d7, latest)

        updated_on_d14 = updated_on - timedelta(days=14)
        value_d14 = dataset.get(updated_on_d14)
        delta_d14 = self.compute_change(value_d14, latest)

        return {
            'updatedOn': updated_on.strftime(DATE_OUT_F),
            'latest': round(latest, 2),
            'percentile': round(percentile, 2),
            'd7Value': round(value_d7, 2),
            'd7DeltaPct': round(delta_d7, 2),
            'd14Value': round(value_d14, 2),
            'd14DeltaPct': round(delta_d14, 2),
        }

    def prep_wastewater(self):
        pass

    def prep_hospital_cases(self):
        pass

    def prep_icu_cases(self):
        pass

    def prep_deaths(self):
        pass

    def compute_percentile(self, value, all_values):
        """Source: https://en.wikipedia.org/wiki/Percentile_rank
        PR = (CF' + (.5 * F)) / N * 100
        CF' (cumulative frequency) is the count of all scores less than the score of interest
        F is the frequency for the score of interest
        N is the number of scores in the distribution
        """
        sorted_values = sorted(all_values)
        cf = sorted_values.index(value)
        freq = sorted_values.count(value)
        return (cf + (.5 * freq)) / len(sorted_values) * 100

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

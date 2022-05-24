from os.path import join as path_join
import csv
from functools import cached_property
import time

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

        # TODO: write dict to file as pretty json

        return self.json_path

    #
    # Private
    #
    def prep_positive_rate_data(self):
        return {
            'updatedOn': '',
            'latest': 0.0,
            'level': '',
            'trend': '',
            'd7Value': 0.0,
            'd7DeltaPct': 0.0,
            'd14Value': 0.0,
            'd14DeltaPct': 0.0,
        }

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

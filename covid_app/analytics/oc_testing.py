from os.path import join as path_join
import queue
from math import floor
from functools import cached_property

from config.app import DATA_ROOT
from covid_app.models.oc.covid_virus_test import CovidVirusTest
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')


class OcTestingAnalysis:
    #
    # Static Methods
    #
    @staticmethod
    def project_specs_forward():
        virus_tests = []

        analysis = OcTestingAnalysis()

        # A simple FIFO queue
        testing_queue = queue.SimpleQueue()
        pos_specs_counted = 0
        skipped_dupes = 0

        # Loop through daily test logs
        for test_log in analysis.daily_test_logs:
            timestamp = test_log['date']
            new_pos_tests_administered = test_log['daily_pos_spec']

            # Collect non-duplicate positive specs for this day
            for n in range(new_pos_tests_administered):
                pos_specs_counted += 1

                # Control for multiple positive tests per case
                if skipped_dupes < analysis.duplicate_specimens:
                    is_dupe = pos_specs_counted % analysis.duplicate_test_odds == 0
                    if is_dupe:
                        skipped_dupes += 1
                        continue

                virus_test = CovidVirusTest(spec_timestamp=timestamp, result='positive')
                testing_queue.put(virus_test)

        # Loop through daily case logs to estimate reporting delays
        for case_log in analysis.daily_case_logs:
            timestamp = case_log['Date']
            new_pos_tests_reported = case_log['daily_cases_repo']

            # Collect non-duplicate positive specs for this day
            for n in range(new_pos_tests_reported):
                waiting_test = testing_queue.get()
                waiting_test.reported_at = timestamp
                virus_tests.append(waiting_test)

        return virus_tests

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

    @property
    def duplicate_specimens(self):
        return self.total_positive_specimens - self.total_cases

    @property
    def duplicate_test_ratio(self):
        return self.duplicate_specimens / self.total_positive_specimens

    @property
    def duplicate_test_odds(self):
        return floor(1 / self.duplicate_test_ratio)

    #
    # Instance Method
    #
    def __init__(self):
        self.logs_by_day = {}
        self.headers = []

    def to_csv(self):
        pass

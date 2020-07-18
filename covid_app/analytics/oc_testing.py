from os.path import join as path_join
import queue
from collections import deque, Counter
from math import floor
from functools import cached_property
from statistics import mean, stdev
import csv

from config.app import DATA_ROOT
from covid_app.models.oc.covid_virus_test import CovidVirusTest
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')
ANALYTICS_FILE = 'oc-tests-reporting.csv'
CSV_COLUMNS = ['Date', 'Administered', 'Reported', 'Avg Days Wait', 'Wait Std Dev',
               'Wait Min', 'Wait Max']


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

    @cached_property
    def dated_virus_tests(self):
        virus_tests = self.backdate_tests_by_date_reported()
        return sorted(virus_tests, key=lambda t: t.administered_on)

    @cached_property
    def administered_tests_by_date(self):
        tests_grouped_by_date = {}

        for virus_test in self.dated_virus_tests:
            if tests_grouped_by_date.get(virus_test.administered_on):
                tests_grouped_by_date[virus_test.administered_on].append(virus_test)
            else:
                tests_grouped_by_date[virus_test.administered_on] = [virus_test]

        return tests_grouped_by_date

    @cached_property
    def reported_tests_by_date(self):
        tests_grouped_by_date = {}

        for virus_test in self.dated_virus_tests:
            if tests_grouped_by_date.get(virus_test.reported_on):
                tests_grouped_by_date[virus_test.reported_on].append(virus_test)
            else:
                tests_grouped_by_date[virus_test.reported_on] = [virus_test]

        return tests_grouped_by_date

    @cached_property
    def dates(self):
        administered_dates = set(self.administered_tests_by_date.keys())
        reported_dates = set(self.reported_tests_by_date.keys())
        return sorted(list(administered_dates | reported_dates))

    @property
    def wait_times(self):
        return [vt.days_to_report for vt in self.dated_virus_tests]

    @property
    def wait_time_frequencies(self):
        return Counter(self.wait_times)

    @property
    def average_days_to_report(self):
        return sum(self.wait_times) / len(self.wait_times)

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
        administered_tests = self.administered_tests_by_date.get(dated, [])
        days_to_report = [t.days_to_report for t in administered_tests]

        tests_administered = len(administered_tests)
        tests_reported = len(self.reported_tests_by_date.get(dated, []))
        days_mean = mean(days_to_report) if len(days_to_report) > 0 else None
        days_stddev = stdev(days_to_report) if len(days_to_report) > 1 else None
        days_min = min(days_to_report) if len(days_to_report) > 0 else None
        days_max = max(days_to_report) if len(days_to_report) > 0 else None

        return [
            dated,
            tests_administered,
            tests_reported,
            days_mean,
            days_stddev,
            days_min,
            days_max
        ]

    def backdate_tests_by_date_reported(self):
        dated_tests = []
        queued_tests = self.queue_positive_tests_by_reported_date()
        queue_empty = False

        for test_log in reversed(self.daily_test_logs):
            if queue_empty:
                break

            administered_at = test_log['date']
            daily_pos_spec = test_log['daily_pos_spec']

            if not daily_pos_spec:
                continue

            # Control for cases with multiple positive tests
            dupe_tests = floor(self.duplicate_test_ratio * daily_pos_spec)
            none_dupe_pos_tests = daily_pos_spec - dupe_tests

            # Collect non-duplicate positive specs for this day
            for n in range(none_dupe_pos_tests):
                try:
                    queued_test = queued_tests.popleft()

                    # Test must be administered before it can be reported
                    timing_nigo = administered_at >= queued_test.reported_at

                    if timing_nigo:
                        queued_tests.appendleft(queued_test)
                    else:
                        queued_test.administered_at = administered_at
                        dated_tests.append(queued_test)
                except IndexError:
                    queue_empty = True
                    break

        return dated_tests

    def queue_positive_tests_by_reported_date(self):
        """Returns deque with tests in DESC order."""
        case_queue = deque()

        for case_log in reversed(self.daily_case_logs):
            reported_at = case_log['Date']
            new_pos_tests_reported = case_log['daily_cases_repo']

            for n in range(new_pos_tests_reported):
                virus_test = CovidVirusTest(reported_at=reported_at, result='positive')
                case_queue.append(virus_test)

        return case_queue

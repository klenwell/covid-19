from os.path import join as path_join
from functools import cached_property
from datetime import timedelta, datetime
import time
import json

from config.app import GH_PAGES_ROOT
from covid_app.extracts.oc_hca.daily_extract import OcHcaDailyExtract
from covid_app.analytics.oc.waves import OcWaveAnalysis


#
# Constants
#
JSON_DATA_PATH = path_join(GH_PAGES_ROOT, 'data', 'json', 'oc')
DATE_OUT_F = '%Y-%m-%d'
JSON_SCHEMA = {
    'data': {},
    'meta': {
        'createdOn': '{date}',
        'lastUpdatedOn': '{date}'
    }
}


class OCWavesExport:
    def __init__(self, test=False):
        self.run_time_start = time.time()
        self.run_time_end = None
        self.test = test

        if self.test:
            print('[WARNING] In test mode: loading sample data.')
            self.case_extract.mock_api_calls()

    #
    # Properties
    #
    # Paths
    @property
    def waves_json_path(self):
        file_name = 'waves.json'
        return path_join(JSON_DATA_PATH, file_name)

    @property
    def data_source_path(self):
        return self.analysis.data_source_path

    # Extracts
    @cached_property
    def analysis(self):
        return OcWaveAnalysis(self.test)

    @cached_property
    def case_extract(self):
        return OcHcaDailyExtract()

    @property
    def epidemic(self):
        return self.analysis.epidemic

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
    def iso_timestamp(self):
        # Source: https://stackoverflow.com/a/28147286/1093087
        return datetime.now().astimezone().replace(microsecond=0).isoformat()

    @property
    def run_time(self):
        if not self.run_time_end:
            self.run_time_end = time.time()

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def waves_to_json_file(self):
        schema = JSON_SCHEMA.copy()

        schema['data'] = self.prep_waves_data()
        schema['meta'] = {
            'createdAt': self.iso_timestamp,
            'lastUpdatedOn': self.analysis.end_date.strftime(DATE_OUT_F)
        }

        # pretty print
        with open(self.waves_json_path, 'w') as f:
            f.write(json.dumps(schema, indent=4))

        return self.waves_json_path

    #
    # Private
    #
    def prep_waves_data(self):
        waves = []

        for wave in self.epidemic.waves:
            total_cases = self.sum_timeline(wave.get_timeline('new_cases'))
            total_deaths = self.sum_timeline(wave.get_timeline('deaths'))
            max_case_avg = self.find_max_date_and_value(wave.get_timeline('avg_new_cases'))
            max_hosps = self.find_max_date_and_value(wave.get_timeline('hospitalizations'), 0)
            max_icus = self.find_max_date_and_value(wave.get_timeline('icu_cases'), 0)
            wave_data = {
                'startedOn': wave.started_on.strftime(DATE_OUT_F),
                'endedOn': wave.ended_on.strftime(DATE_OUT_F),
                'type': 'wave' if wave.is_wave() else 'lull',
                'days': wave.days,
                'peakedOn': wave.peaked_on.strftime(DATE_OUT_F),
                'maxPositiveRate': {
                    'date': wave.peaked_on.strftime(DATE_OUT_F),
                    'value': round(wave.peak_value, 2)
                },
                'minPositiveRate': {
                    'date': wave.floored_on.strftime(DATE_OUT_F),
                    'value': round(wave.floor_value, 2)
                },
                'maxCaseAvg': max_case_avg,
                'maxHospitalizations': max_hosps,
                'maxIcuCases': max_icus,
                'totalTests': sum(wave.get_timeline('tests_admin').values()),
                'totalPositiveTests': sum(wave.get_timeline('tests_positive').values()),
                'totalCases': total_cases,
                'totalDeaths': total_deaths,
                'datasets': {
                    'dates': [d.strftime(DATE_OUT_F) for d in sorted(wave.timeline.keys())],
                    'avgPositiveRates': self.to_dataset(wave.timeline),
                    'tests': self.to_dataset(wave.get_timeline('tests_admin')),
                    'positiveTests': self.to_dataset(wave.get_timeline('tests_positive')),
                    'avgCases': self.to_dataset(wave.get_timeline('avg_new_cases'))
                }

            }
            waves.append(wave_data)

        return waves

    def find_max_date_and_value(self, timeline, precision=2):
        values = [v for v in timeline.values() if v is not None]
        max_value = max(values)
        for dated, value in timeline.items():
            if value == max_value:
                value = round(value, precision) if precision is not None else value
                return {'date': dated.strftime(DATE_OUT_F), 'value': value}

    def sum_timeline(self, timeline):
        values = [v for v in timeline.values() if v is not None]
        return sum(values)

    def to_dataset(self, timeline, precision=2):
        """Converts dict {date: value...} to list of values (correlated to date list).
        """
        dataset = []
        for dated in sorted(timeline.keys()):
            value = timeline[dated]
            value = round(value, precision) if precision is not None else value
            dataset.append(value)
        return dataset

    def week_avg_from_date(self, daily_values, from_date):
        values = []
        for n in range(7):
            dated = from_date - timedelta(days=n)
            value = daily_values[dated]
            values.append(value)
        return sum(values) / len(values)

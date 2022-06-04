from os.path import join as path_join
from functools import cached_property
from datetime import timedelta
import time
import json

from config.app import GH_PAGES_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.analytics.oc.waves import OcWaveAnalysis

#
# Constants
#
JSON_DATA_PATH = path_join(GH_PAGES_ROOT, 'data', 'json', 'oc')
JSON_FILE_NAME = 'waves.json'

JSON_SCHEMA = {
    'waves': [],
    'phases': []
}

DATE_OUT_F = '%Y-%m-%d'


class OCWavesExport:
    #
    # Properties
    #
    @property
    def json_path(self):
        return path_join(JSON_DATA_PATH, JSON_FILE_NAME)

    # Extracts
    @cached_property
    def analysis(self):
        return OcWaveAnalysis(self.test)

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

        if self.test:
            print('[WARNING] In test mode: loading sample data.')
            self.case_extract.mock_api_calls()

    def to_json_file(self):
        schema = JSON_SCHEMA.copy()

        schema['waves'] = self.prep_waves_data()
        schema['phases'] = self.prep_phases_cases()

        # pretty print
        with open(self.json_path, 'w') as f:
            f.write(json.dumps(schema, indent=4))

        return self.json_path

    #
    # Private
    #
    def prep_waves_data(self):
        waves = []

        for wave in self.analysis.epidemic.waves:
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
                    'date': wave.peaked_on.strftime(DATE_OUT_F),
                    'value': round(wave.peak_value, 2)
                },
                'maxDailyCases': {},
                'maxHospitalizations': {},
                'rateTimeSeries': self.to_timeseries(wave.timeline),
                'totalTests': None,
                'positiveTests': None,
                'cases': None,
                'hospitalizations': None,
                'icus': None,
                'deaths': None
            }
            waves.append(wave_data)
        return waves

    def prep_phases_cases(self):
        pass

    def to_timeseries(self, timeline):
        """Converts dict {date: value...} to ordered list [(date, value)...]
        """
        time_series = []
        for dated in sorted(timeline.keys()):
            value = round(timeline[dated], 2)
            time_series.append((dated.strftime(DATE_OUT_F), value))
        return time_series

    def week_avg_from_date(self, daily_values, from_date):
        values = []
        for n in range(7):
            dated = from_date - timedelta(days=n)
            value = daily_values[dated]
            values.append(value)
        return sum(values) / len(values)

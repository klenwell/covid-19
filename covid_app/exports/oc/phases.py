from os.path import join as path_join
from functools import cached_property
from datetime import timedelta, datetime
import time
import json

from config.app import GH_PAGES_ROOT
from covid_app.analytics.oc.waves import OcWaveAnalysis


#
# Constants
#
JSON_DATA_PATH = path_join(GH_PAGES_ROOT, 'data', 'json', 'oc')
DATE_OUT_F = '%Y-%m-%d'
JSON_SCHEMA = {
    'phases': {},
    'meta': {
        'createdOn': '{date}',
        'lastUpdatedOn': '{date}'
    }
}


class OCPhasesExport:
    def __init__(self, test=False):
        self.run_time_start = time.time()
        self.run_time_end = None
        self.test = test

    #
    # Properties
    #
    # Paths
    @property
    def json_path(self):
        file_name = 'phases.json'
        return path_join(JSON_DATA_PATH, file_name)

    @property
    def data_source_path(self):
        return self.analysis.data_source_path

    # Extracts
    @cached_property
    def analysis(self):
        return OcWaveAnalysis(self.test)

    @property
    def epidemic(self):
        return self.analysis.epidemic

    # Data
    def phases(self):
        return self.analysis.epidemic.smoothed_phases

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
    def phases_to_json_file(self):
        schema = JSON_SCHEMA.copy()

        schema['data'] = self.prep_phases_data()
        schema['meta'] = {
            'createdAt': self.iso_timestamp,
            'lastUpdatedOn': self.analysis.end_date.strftime(DATE_OUT_F)
        }

        # pretty print
        with open(self.json_path, 'w') as f:
            f.write(json.dumps(schema, indent=4))

        return self.json_path

    #
    # Private
    #
    def prep_phases_data(self):
        phases = []

        for phase in self.phases:
            total_cases = self.sum_timeline(phase.get_timeline('new_cases'))
            total_deaths = self.sum_timeline(phase.get_timeline('deaths'))
            max_case_avg = self.find_max_date_and_value(phase.get_timeline('avg_new_cases'))
            max_hosps = self.find_max_date_and_value(phase.get_timeline('hospitalizations'), 0)
            max_icus = self.find_max_date_and_value(phase.get_timeline('icu_cases'), 0)
            phase_data = {
                'startedOn': phase.started_on.strftime(DATE_OUT_F),
                'endedOn': phase.ended_on.strftime(DATE_OUT_F),
                'trend': phase.trending,
                'days': phase.days,
                'peakedOn': phase.peaked_on.strftime(DATE_OUT_F),
                'maxPositiveRate': {
                    'date': phase.peaked_on.strftime(DATE_OUT_F),
                    'value': round(phase.peak_value, 2)
                },
                'minPositiveRate': {
                    'date': phase.floored_on.strftime(DATE_OUT_F),
                    'value': round(phase.floor_value, 2)
                },
                'maxCaseAvg': max_case_avg,
                'maxHospitalizations': max_hosps,
                'maxIcuCases': max_icus,
                'totalTests': sum(phase.get_timeline('tests_admin').values()),
                'totalPositiveTests': sum(phase.get_timeline('tests_positive').values()),
                'totalCases': total_cases,
                'totalDeaths': total_deaths,
                'datasets': {
                    'dates': [d.strftime(DATE_OUT_F) for d in sorted(phase.timeline.keys())],
                    'avgPositiveRates': self.to_dataset(phase.timeline),
                    'tests': self.to_dataset(phase.get_timeline('tests_admin')),
                    'positiveTests': self.to_dataset(phase.get_timeline('tests_positive')),
                    'avgCases': self.to_dataset(phase.get_timeline('avg_new_cases'))
                }

            }
            phases.append(phase_data)

        return phases

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

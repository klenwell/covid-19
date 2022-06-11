from os.path import join as path_join
from functools import cached_property
from datetime import timedelta, datetime
import time
import json

from config.app import GH_PAGES_ROOT, OC_POPULATION
from covid_app.analytics.oc.waves import OcWaveAnalysis


#
# Constants
#
JSON_DATA_PATH = path_join(GH_PAGES_ROOT, 'data', 'json', 'oc')
DATE_OUT_F = '%Y-%m-%d'
JSON_SCHEMA = {
    'phases': {},
    'meta': {
        'createdAt': '{date}',
        'dataLastUpdated': '{date}'
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
    @cached_property
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
    def to_json_file(self):
        schema = JSON_SCHEMA.copy()

        schema['phases'] = self.prep_phases_data()
        schema['meta'] = {
            'createdAt': self.iso_timestamp,
            'dataLastUpdated': self.analysis.end_date.strftime(DATE_OUT_F)
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
            avg_pos_rate = phase.timeline
            phase_data = {
                'startedOn': phase.started_on.strftime(DATE_OUT_F),
                'endedOn': phase.ended_on.strftime(DATE_OUT_F),
                'trend': phase.trending,
                'days': phase.days,
                'startPositiveRate': avg_pos_rate[phase.started_on],
                'endPositiveRate': avg_pos_rate[phase.ended_on],
                'popSlope': phase.slope * OC_POPULATION,
                'datasets': {
                    'dates': [d.strftime(DATE_OUT_F) for d in sorted(phase.timeline.keys())],
                    'avgPositiveRates': self.to_dataset(phase.timeline),
                    'avgCases': self.to_dataset(phase.get_timeline('avg_new_cases'))
                }
            }
            phases.append(phase_data)

        return phases

    def to_dataset(self, timeline, precision=2):
        """Converts dict {date: value...} to list of values (correlated to date list).
        """
        dataset = []
        for dated in sorted(timeline.keys()):
            value = timeline[dated]
            value = round(value, precision) if precision is not None else value
            dataset.append(value)
        return dataset

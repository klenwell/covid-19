from os.path import join as path_join
from functools import cached_property
from datetime import datetime, timedelta
from math import floor, inf
import time
import csv
import statistics
from pprint import pprint, pformat

from config.app import DATA_ROOT
from covid_app.models.oc.epidemic_wave import EpidemicWave


#
# Constants
#
DATE_F = '%Y-%m-%d'
START_DATE = '2020-03-05'
WINDOW_SIZE = 5             # Must be odd number!
MICRO_INTERVAL_MAX = 14
KSLOPE_THRESHOLD = 5        # Slope value distinguishing plateaus from rise/falls
SAMPLE_DATA_CSV = path_join(DATA_ROOT, 'samples', 'oc-rates.csv')



class OcWaveAnalysis:
    #
    # Properties
    #
    @cached_property
    def wave(self):
        opts = {
            'window_size': 5,
            'flat_slope_threshold': 5,
            'min_phase_size': 14
        }
        return EpidemicWave(self.avg_positive_rates, **opts)

    @cached_property
    def avg_positive_rates(self):
        if self.test:
            return self.test_avg_positive_rates

        dated_values = {}

        for dated in self.dates:
            tests = []
            positives = []
            for days_back in range(7):
                prev_date = dated - timedelta(days=days_back)
                tests.append(self.tests_admin[prev_date])
                positives.append(self.tests_positive[prev_date])
            dated_values[dated] = sum(positives) / sum(tests) * 100

        return dated_values

    @cached_property
    def test_avg_positive_rates(self):
        dated_values = {}
        with open(SAMPLE_DATA_CSV, newline='') as f:
            for row in csv.reader(f):
                dated = datetime.strptime(row[0], DATE_F).date()
                dated_values[dated] = float(row[1])
        return dated_values

    @cached_property
    def tests_admin(self):
        dated_values = {}
        for dated in self.dated_export_rows.keys():
            try:
                dated_values[dated] = int(self.dated_export_rows[dated]['Tests Admin'])
            except ValueError:
                pass
        return dated_values

    @cached_property
    def tests_positive(self):
        dated_values = {}
        for dated in self.dated_export_rows.keys():
            try:
                dated_values[dated] = int(self.dated_export_rows[dated]['Pos Tests Admin'])
            except ValueError:
                pass
        return dated_values

    @property
    def daily_oc_export_path(self):
        return path_join(DATA_ROOT, 'oc', 'oc-hca.csv')

    @cached_property
    def export_rows(self):
        with open(self.daily_oc_export_path, newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows

    @cached_property
    def dated_export_rows(self):
        export_rows = {}
        for row in self.export_rows:
            dated = datetime.strptime(row['Date'], DATE_F).date()
            export_rows[dated] = row
        return export_rows

    # Dates
    @property
    def dates(self):
        num_days = (self.end_date - self.start_date).days
        return [self.start_date + timedelta(days=n) for n in range(num_days + 1)]

    @property
    def start_date(self):
        return datetime.strptime(START_DATE, DATE_F).date()

    @property
    def end_date(self):
        for row in self.export_rows:
            try:
                int(row['Tests Admin']) and int(row['Pos Tests Admin'])
                return datetime.strptime(row['Date'], DATE_F).date()
            except ValueError:
                pass

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

    def windows_to_csv(self):
        csv_path = path_join(DATA_ROOT, 'oc', 'analytics', 'windows.csv')
        headers = ['date', 'rate', 'stdev', 'rsd', 'slope', 'mean', 'change', 'trend']
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for dated, row in sorted(self.wave.windows.items()):
                writer.writerow([
                    dated,
                    row['rate'],
                    row['stdev'],
                    row['rsd'],
                    row['slope'],
                    row['mean'],
                    row['change'],
                    row['trend']
                ])

        self.run_time_end = time.time()
        print(self.run_time, csv_path)
        return csv_path

    def export_sample_data_to_csv(self):
        start_date = datetime.strptime('2020-10-01', DATE_F).date()
        end_date = datetime.strptime('2021-11-01', DATE_F).date()

        with open(SAMPLE_DATA_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            next_date = start_date

            while next_date <= end_date:
                writer.writerow([
                    next_date,
                    self.avg_positive_rates[next_date]
                ])
                next_date += timedelta(days=1)

        print('export_sample_data_to_csv', SAMPLE_DATA_CSV)
        return SAMPLE_DATA_CSV

    def export_windows_and_phases_to_csv(self):
        headers = ['date', 'rate', 'window', 'phase']
        csv_name = "waves-w{}-p{}-s{}.csv".format(self.wave.window_size,
            self.wave.min_phase_size, self.wave.flat_slope_threshold)
        csv_path = path_join(DATA_ROOT, 'tmp', csv_name)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for dated in self.wave.dates:
                phase = [p for p in self.wave.smoothed_phases if p.started_on == dated]
                window = [w for w in self.wave.windows if w.date == dated]

                writer.writerow([
                    dated,
                    self.avg_positive_rates[dated],
                    window[0].value if window else '',
                    phase[0].start_value if phase else ''
                ])

        return csv_path

    #
    # Private
    #
    def compute_change(self, old, new):
        """Source: https://stackoverflow.com/q/30926840/1093087
        """
        return (new - old) / old * 100.0
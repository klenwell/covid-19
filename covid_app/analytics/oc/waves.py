from os.path import join as path_join
from functools import cached_property
from datetime import datetime, timedelta
import time
import csv

from config.app import DATA_ROOT


#
# Constants
#
DATE_F = '%Y-%m-%d'
START_DATE = '2020-02-01'
TREND_THRESHOLD = 8
UP_TREND = 1
DOWN_TREND = -1
FLAT_TREND = 0


class OcWaveAnalysis:
    #
    # Properties
    #
    @cached_property
    def intervals(self):
        intervals = []
        for row in self.trends:
            if row['trend_change']:
                intervals.append(row)
        return intervals

    @cached_property
    def trends(self):
        rows = []
        prev_trend = None

        # Skip start date since need to look back
        for dated in self.dates:
            date_m1 = dated - timedelta(days=1)
            date_m14 = dated - timedelta(days=1)

            pos_rate = self.avg_positive_rates[dated]
            d1_pos_rate = self.avg_positive_rates.get(date_m1)
            d14_pos_rate = self.avg_positive_rates.get(date_m14)

            if not d14_pos_rate:
                continue

            d1_delta = self.compute_change(d1_pos_rate, pos_rate)
            d14_delta = self.compute_change(d14_pos_rate, pos_rate)
            trend = self.map_rate_trend(d14_delta)
            trend_change = prev_trend is not None and trend != prev_trend

            row = {
                'date': dated,
                'rate': pos_rate,
                'd1-delta': d1_delta,
                'd14-delta': d14_delta,
                'trend': trend,
                'trend_change': trend_change
            }

            prev_trend = trend
            rows.append(row)

        return rows

    def map_rate_trend(self, delta):
        if delta >= TREND_THRESHOLD:
            return UP_TREND
        elif delta <= -TREND_THRESHOLD:
            return DOWN_TREND
        else:
            return FLAT_TREND

    @cached_property
    def avg_positive_rates(self):
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

    # Date sets
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

    #
    # Private
    #
    def compute_change(self, old, new):
        """Source: https://stackoverflow.com/q/30926840/1093087
        """
        return (new - old) / old * 100.0

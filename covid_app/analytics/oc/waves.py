from os.path import join as path_join
from functools import cached_property
from datetime import datetime, timedelta
from math import floor
import time
import csv
import statistics
from pprint import pprint

from config.app import DATA_ROOT


#
# Constants
#
DATE_F = '%Y-%m-%d'
START_DATE = '2020-02-01'
WINDOW_SIZE = 7
KSLOPE_THRESHOLD = 10   # Slope value distinguishing plateaus from rise/falls
SAMPLE_DATA_CSV = path_join(DATA_ROOT, 'samples', 'oc-rates.csv')


from itertools import islice
from collections import deque
def sliding_window(iterable, n):
    """Source: https://docs.python.org/3/library/itertools.html#itertools-recipes
    sliding_window('ABCDEFG', 4) -> ABCD BCDE CDEF DEFG
    """
    it = iter(iterable)
    window = deque(islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for x in it:
        window.append(x)
        yield tuple(window)


class Window:
    def __init__(self, dated, rates):
        self.date = dated
        self.rates = rates
        self.rate = rates[floor(len(rates) / 2)]

    @property
    def rate_change(self):
        return self.rates[-1] - self.rates[0]

    @property
    def slope(self):
        return self.rate_change / len(self.rates)

    @property
    def kslope(self):
        return self.slope * 100

    @property
    def stdev(self):
        return statistics.stdev(self.rates)

    @property
    def trend(self):
        if self.kslope > KSLOPE_THRESHOLD:
            return 1
        elif self.kslope < -KSLOPE_THRESHOLD:
            return -1
        else:
            return 0

    def __repr__(self):
        f = '<Window middate={} days={} kslope={:.1f} stdev={:.3f} trend={}>'
        return f.format(self.date, len(self.rates), self.kslope, self.stdev, self.trend)


class Interval:
    @staticmethod
    def includes_micros(intervals):
        for interval in intervals:
            if interval.is_micro():
                return True
        return False

    @staticmethod
    def smooth_intervals(intervals):
        n = 0
        while Interval.includes_micros(intervals):
            n += 1
            print('micro merge loop', n, len(intervals))
            pprint(intervals)
            pre_merge_count = len(intervals)
            intervals = Interval.merge_intervals(intervals)

            if Interval.includes_micros(intervals) and len(intervals) == pre_merge_count:
                raise Exception('Unable to merge micro intervals: {}'.format(intervals))

        return intervals

    @staticmethod
    def merge_intervals(intervals):
        merged_intervals = []
        prev_interval = None
        merge_with_prev = False
        merge_with_next = False

        for interval, next_interval in sliding_window(intervals, 2):
            #print(prev_interval, interval, next_interval)
            merge_with_prev = False     # reset flag each loop

            # In previous loop, flagged that interval to merge with this one.
            if merge_with_next:
                interval = interval.merge(prev_interval)
                merge_with_next = False

            if not interval.is_micro():
                merged_intervals.append(interval)
                prev_interval = interval
                continue

            # What to do with micro interval?
            # If it trends with previous, merge
            if interval.trend == prev_interval.trend:
                merge_with_prev = True

            # If it trends with next, flag for merge in next loop
            elif interval.trend == next_interval.trend:
                merge_with_next = True

            # If flat, merge with previous or next
            elif interval.trending == 'flat':
                slope_diff_prev = interval.kslope - prev_interval.kslope
                slope_diff_next = interval.kslope - next_interval.kslope
                if slope_diff_prev > slope_diff_next:
                    merge_with_prev = True
                else:
                    merge_with_next = True

            else:
                raise ValueError("Orphaned micro interval: {}".format(interval))

            # Merge with previous if flagged above
            if merge_with_prev:
                interval = interval.merge(prev_interval)

                # If prev interval was added to smooth, pop and replace with merged one
                if prev_interval in merged_intervals:
                    merged_intervals.pop()

                merged_intervals.append(interval)

            # on to next loop
            prev_interval = interval

        # Don't forget last interval
        merged_intervals.append(intervals[-1])

        return merged_intervals

    def __init__(self, start_window):
        self.start_window = start_window
        self.end_window = None

    @property
    def started_on(self):
        return self.start_window.date

    @property
    def ended_on(self):
        if self.is_ended:
            return self.end_window.date

    @property
    def start_rate(self):
        return self.start_window.rate

    @property
    def end_rate(self):
        if self.is_ended:
            return self.end_window.rate

    @property
    def is_ended(self):
        return self.end_window is not None

    @property
    def days(self):
        if not self.is_ended:
            return None
        return (self.ended_on - self.started_on).days

    @property
    def rate_diff(self):
        if not self.is_ended:
            return None
        return self.end_rate - self.start_rate

    @property
    def kslope(self):
        if not self.is_ended:
            return None
        return self.rate_diff / self.days * 100

    @property
    def trend(self):
        if self.kslope is None:
            return None

        if self.kslope > KSLOPE_THRESHOLD:
            return 1
        elif self.kslope < -KSLOPE_THRESHOLD:
            return -1
        else:
            return 0

    @property
    def trending(self):
        labels = {
            -1: 'falling',
            0: 'flat',
            1: 'rising'
        }
        if self.trend is not None:
            return labels[self.trend]

    # Methods
    def merge(self, other_interval):
        start_interval = self if self.started_on < other_interval.started_on else other_interval
        end_interval = self if start_interval != self else other_interval
        merged_interval = Interval(start_interval.start_window)
        merged_interval.end(end_interval.end_window)
        return merged_interval

    def end(self, window):
        self.end_window = window

    def is_micro(self):
        if not self.is_ended:
            return None

        if self.days <= 14:
            return True

        return False

    def __repr__(self):
        f = '<Interval start={} end={} days={} kslope={} trending={} micro?={}>'
        kslope = None if self.kslope is None else round(self.kslope, 1)
        return f.format(self.started_on, self.ended_on, self.days, kslope, self.trending,
            self.is_micro())


class OcWaveAnalysis:
    #
    # Properties
    #
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
    def smooth_intervals(self):
        return Interval.smooth_intervals(self.intervals)

    @cached_property
    def intervals(self):
        intervals = []
        prev_window = self.windows[0]
        open_interval = Interval(prev_window)

        for window in self.windows[1:]:
            trend_change = window.trend != prev_window.trend

            if trend_change:
                open_interval.end(window)
                intervals.append(open_interval)
                open_interval = Interval(window)

            prev_window = window

        if open_interval.start_window != window:
            open_interval.end(window)
            intervals.append(open_interval)

        return intervals

    @cached_property
    def windows(self):
        windows = []
        half_window_len = floor(WINDOW_SIZE / 2)

        for dated in self.dates:
            window_rates = []

            for n in range(-half_window_len, half_window_len+1):
                rate_date = dated + timedelta(days=n)
                rate = self.avg_positive_rates.get(rate_date)
                if rate:
                    window_rates.append(rate)

            if len(window_rates) == WINDOW_SIZE:
                window = Window(dated, window_rates)
                windows.append(window)

        return windows

    @cached_property
    def std_devs(self):
        dated_values = {}

        for dated in self.dates[1:]:
            yesterday = dated - timedelta(days=1)
            window = self.windows.get(yesterday)

            if not window:
                continue

            diff = self.avg_positive_rates[dated] - window['mean']
            dev = diff / window['stdev']
            dated_values[dated] = dev

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

            for dated, row in sorted(self.windows.items()):
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

    #
    # Private
    #
    def compute_change(self, old, new):
        """Source: https://stackoverflow.com/q/30926840/1093087
        """
        return (new - old) / old * 100.0

"""
Class for breaking a data series (e.g. positive rate data) into waves and troughs.

An epidemic is made up of waves which are made up of phases which are made up of
phase windows which are made up of data points (from a time series.)
"""
from functools import cached_property
from datetime import timedelta, date
from math import floor, inf
from pprint import pformat
from itertools import islice
from collections import deque

from config.app import WAVE_ANALYSIS_CONFIG
from covid_app.models.oc.epidemic_wave import EpidemicWave
from covid_app.models.oc.wave_phase import WavePhase
from covid_app.models.oc.phase_window import PhaseWindow


class PhaseSmoothingError(Exception):
    def __init__(self, phases):
        message = 'Unable to smooth jagged phases:\n {}'.format(pformat(phases))
        super().__init__(message)
        self.phases = phases


class PhaseMergingError(Exception):
    def __init__(self, prev_phase, phase):
        message = 'Unexpected phase combination:\nphase: {}\nprev:{}'.format(
            phase, prev_phase)
        super().__init__(message)


class WaveExtractionError(Exception):
    def __init__(self, prev_phase, next_phase):
        message = 'Unexpected phase combination:\n{}\n{}'.format(prev_phase, next_phase)
        super().__init__(message)


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


class Epidemic:
    def __init__(self, time_series, opts=None, datasets=None):
        """Datasets is dict of dicts mapping dates to values. They get added as timelines
        mapping dates (in time_series date range) to values. Example:

        datasets = {'key1': {<date>: 1.2, <date>:2.5, ...}, 'key2': timeseries2}
        """
        self.timeline = time_series
        self.timelines = {
            'primary': time_series
        }

        # Opts
        c = WAVE_ANALYSIS_CONFIG
        opts = opts if opts is not None else {}
        self.debug = opts.get('debug', False)
        self.window_size = opts.get('window_size', c['window_size'])
        self.flat_slope_threshold = opts.get('flat_slope_threshold', c['flat_slope_threshold'])
        self.min_phase_size = opts.get('min_phase_size', c['min_phase_size'])

        # Datasets
        datasets = datasets if datasets is not None else {}
        for key, dataset in datasets.items():
            self.add_timeline(key, dataset)

    #
    # Properties
    #
    @cached_property
    def waves(self):
        return self.generate_waves(self.smoothed_phases)

    @cached_property
    def smoothed_phases(self):
        return self.smooth_phases(self.phases)

    @cached_property
    def phases(self):
        phases = []
        prev_window = self.windows[0]
        open_phase = WavePhase(prev_window, self)

        for window in self.windows[1:]:
            trend_change = window.trend != prev_window.trend

            if trend_change:
                open_phase.end(window)
                phases.append(open_phase)
                open_phase = WavePhase(window, self)
            else:
                open_phase.add_window(window)

            prev_window = window

        if open_phase.start_window != window:
            open_phase.end(window)
            phases.append(open_phase)

        return phases

    @cached_property
    def windows(self):
        windows = []
        half_window_len = floor(self.window_size / 2)

        for dated in self.dates:
            window_rates = []

            for n in range(-half_window_len, half_window_len+1):
                window_date = dated + timedelta(days=n)
                rate = self.timeline.get(window_date)
                if rate:
                    window_rates.append(rate)

            if len(window_rates) == self.window_size:
                window = PhaseWindow(dated, window_rates)
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
    def dates(self):
        return sorted(self.timeline.keys())

    #
    # Methods
    #
    def add_timeline(self, key, time_series):
        timeline = {}
        for dated in self.dates:
            timeline[dated] = time_series.get(dated)
        self.timelines[key] = timeline
        return timeline

    def extract_timeline_by_start_end_dates(self, time_series, start_date, end_date):
        """Extract timeline for time series datapoints falling within range of the
        start and end date.

        This is useful for nested classes: waves and phases
        """
        timeline = {}

        # This will leave any gaps from timeseries in timeline. That's better for graphing.
        for dated, value in sorted(time_series.items()):
            if dated > end_date:
                return timeline

            if dated >= start_date:
                timeline[dated] = value

        return timeline

    def generate_waves(self, phases):
        waves = []
        prev_phase = []
        wave_phases = []

        # If first phase is falling, skip
        first_phase = phases[0]
        if not first_phase.is_falling():
            prev_phase = first_phase
            wave_phases = [prev_phase]
            remaining_phases = phases[1:]
        else:
            remaining_phases = phases

        # Collect waves and lulls
        for phase in remaining_phases:
            # print('generate_waves', prev_phase, phase)
            # New wave
            if prev_phase.is_falling() and phase.is_rising():
                wave_phases.append(phase)
            elif prev_phase.is_flat() and phase.is_rising():
                wave_phases.append(phase)
            # Lull
            elif phase.is_flat():
                wave = EpidemicWave([phase], self)
                waves.append(wave)
                wave_phases = []
            # End wave
            elif prev_phase.is_rising() and phase.is_falling():
                wave_phases.append(phase)
                wave = EpidemicWave(wave_phases, self)
                waves.append(wave)
                wave_phases = []
            # Should not see this case
            else:
                raise WaveExtractionError(prev_phase, phase)

            prev_phase = phase

        # A new wave?
        if len(wave_phases) > 0:
            wave = EpidemicWave(wave_phases, self)
            waves.append(wave)

        return waves

    def smooth_phases(self, phases):
        def log(msg, n, seq): self.debug and print(msg, n, len(seq), "\n", pformat(seq))
        series_is_jagged = self.phase_series_is_jagged(phases)
        n = 0

        # It's tough to get the first drop right algorithmically. So we cheat and hardcode it.
        phases = self.merge_fixed_phase(phases, date(2020, 3, 31), date(2020, 5, 24))
        #breakpoint()

        while series_is_jagged:
            n += 1
            pre_merge_count = len(phases)

            phases = self.merge_running_trends(phases)
            log('post running merges', n, phases)
            phases = self.merge_micro_phases(phases)
            log('post micro merges', n, phases)

            series_is_jagged = self.phase_series_is_jagged(phases)
            if series_is_jagged and len(phases) == pre_merge_count:
                raise PhaseSmoothingError(phases)

        return phases

    def merge_fixed_phase(self, phases, start_date, end_date):
        merged_phases = []

        for n, phase in enumerate(phases):
            if phase.started_on == start_date:
                fixed_phase = phase
            elif phase.started_on > start_date and phase.started_on < end_date:
                fixed_phase = fixed_phase.merge(phase)
            else:
                merged_phases.append(phase)

        merged_phases.append(fixed_phase)
        return sorted(merged_phases, key=lambda p: p.started_on)

    def phase_series_is_jagged(self, phases):
        """These things are considered unjagged or unsmooth:
        - any micro phases (except last)
        - any consecutive phases with same trend
        """
        prev_phase = None
        for phase in phases[:-2]:
            if phase.is_micro():
                return True
            if prev_phase and prev_phase.trend == phase.trend:
                return True
            prev_phase = phase
        return False

    def merge_running_trends(self, phases):
        merged_phases = []
        prev_phase = phases[0]

        for phase in phases[1:]:
            if phase.trend == prev_phase.trend:
                phase = phase.merge(prev_phase)
            else:
                merged_phases.append(prev_phase)
            prev_phase = phase

        # Don't forget last phase
        merged_phases.append(phase)
        return merged_phases

    def merge_micro_phases(self, phases):
        # merge_nearest_micro_phase
        merged_phases = []

        def diff_phases(p1, p2):
            return abs(p2 - p1)

        # Find the micro phases with the smallest slope diff with neighbor
        phase_diffs = []
        for n in range(len(phases) - 1):
            phase = phases[n]
            next_phase = phases[n + 1]
            if not phase.is_micro():
                continue

            phase_diff = diff_phases(phase.slope, next_phase.slope)
            phase_diffs.append((phase_diff, n))

        if len(phase_diffs) < 1:
            return phases

        sorted_phase_diffs = sorted(phase_diffs, key=lambda d: d[0])
        merge_at = sorted_phase_diffs[0][1]
        #print(merge_at, sorted_phase_diffs)

        # Now merge those 2 phases with smallest slope diff
        for n, phase in enumerate(phases):
            if n == merge_at:
                next_phase = phases[n + 1]
                phase = phase.merge(next_phase)
                merged_phases.append(phase)
            elif n == merge_at + 1:
                continue
            else:
                merged_phases.append(phase)

        return merged_phases

    def merge_micro_phases_v1(self, phases):
        merged_phases = []
        prev_phase = None
        merge_on_next_loop = False

        for phase, next_phase in sliding_window(phases, 2):
            # print(prev_phase, phase, next_phase)
            merge_with_prev = False     # reset flag each loop

            # Merge phases as flagged in previous loop.
            if merge_on_next_loop:
                merge_on_next_loop = False
                phase = phase.merge(prev_phase)

                # If prev phase was added to merged_phases, pop and replace with new one below.
                if prev_phase in merged_phases:
                    merged_phases.pop()

            # phase no longer micro, continue to next one
            if not phase.is_micro():
                merged_phases.append(phase)
                prev_phase = phase
                continue

            # Now figure out what to do with micro phases.
            prev_phase_slope = prev_phase.slope if prev_phase is not None else inf
            prev_phase_flatter = abs(prev_phase_slope) < abs(next_phase.slope)
            prev_phase_higher = prev_phase and prev_phase.end_value > next_phase.end_value

            # If no previous, just merge with next phase
            if not prev_phase:
                merge_on_next_loop = True
            # If flat, merge with whichever neighbor is flatter
            elif phase.is_flat():
                if prev_phase_flatter:
                    merge_with_prev = True
                else:
                    merge_on_next_loop = True
            # Continue rising or falling trend
            elif phase.is_rising() and prev_phase.is_rising():
                merge_with_prev = True
            elif phase.is_falling() and prev_phase.is_falling():
                merge_with_prev = True
            # If next phase is higher than previous, merge with next since this should extend trend
            elif phase.is_rising():
                if not prev_phase_higher:
                    merge_on_next_loop = True
                else:
                    merge_with_prev = True
            # Same logic as rising reversed
            elif phase.is_falling():
                if prev_phase_higher:
                    merge_on_next_loop = True
                else:
                    merge_with_prev = True
            else:
                raise PhaseMergingError(prev_phase, phase)

            # Merge with previous if flagged above
            if merge_with_prev:
                phase = phase.merge(prev_phase)
                if prev_phase in merged_phases:
                    merged_phases.pop()

            if not merge_on_next_loop:
                merged_phases.append(phase)

            # on to next loop
            prev_phase = phase

        # Don't forget last phase. If micro just merge with previous.
        last_phase = phases[-1]
        if last_phase.is_micro():
            last_merged_phase = merged_phases.pop()
            last_merged_phase = last_merged_phase.merge(last_phase)
            merged_phases.append(last_merged_phase)
        else:
            merged_phases.append(phases[-1])

        return merged_phases

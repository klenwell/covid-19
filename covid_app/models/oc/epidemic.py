"""
Class for breaking a data series (e.g. positive rate data) into waves and troughs.

An epidemic is made up of waves which are made up of phases which are made up of
phase intervals which are made up of data points (from a time series.)
"""
from functools import cached_property
from datetime import timedelta
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
    def __init__(self, time_series, **opts):
        self.time_series = time_series
        self.debug = opts.get('debug', False)
        self.window_size = opts.get('window_size', WAVE_ANALYSIS_CONFIG['window_size'])
        self.flat_slope_threshold = opts.get('flat_slope_threshold',
                                             WAVE_ANALYSIS_CONFIG['flat_slope_threshold'])
        self.min_phase_size = opts.get('min_phase_size',
                                       WAVE_ANALYSIS_CONFIG['min_phase_size'])

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
        open_phase = WavePhase(prev_window)

        for window in self.windows[1:]:
            trend_change = window.trend != prev_window.trend

            if trend_change:
                open_phase.end(window)
                phases.append(open_phase)
                open_phase = WavePhase(window)

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
                rate_date = dated + timedelta(days=n)
                rate = self.time_series.get(rate_date)
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
        return sorted(self.time_series.keys())

    #
    # Methods
    #
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
                wave_phases = [phase]
            elif prev_phase.is_flat() and phase.is_rising():
                wave_phases = [phase]
            # Lull
            elif phase.is_flat():
                wave = EpidemicWave([phase], self.time_series)
                waves.append(wave)
            # End wave
            elif prev_phase.is_rising() and phase.is_falling():
                wave_phases.append(phase)
                wave = EpidemicWave(wave_phases, self.time_series)
                waves.append(wave)
            # Should not see this case
            else:
                raise WaveExtractionError(prev_phase, phase)

            prev_phase = phase

        # A new wave?
        if len(wave_phases) > 0:
            wave = EpidemicWave(wave_phases, self.time_series)
            waves.append(wave)

        return waves

    def smooth_phases(self, phases):
        def log(msg, n, seq): self.debug and print(msg, n, len(seq), "\n", pformat(seq))
        series_is_jagged = self.phase_series_is_jagged(phases)
        n = 0

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

    def phase_series_is_jagged(self, phases):
        """These things are considered unjagged or unsmooth:
        - any micro phases
        - any consecutive phases with same trend
        """
        prev_phase = None
        for phase in phases[:-1]:
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

                # If prev phase was added to smooth, pop and replace with merged one
                if prev_phase in merged_phases:
                    merged_phases.pop()

            # phase no longer micro, continue to next one
            if not phase.is_micro():
                merged_phases.append(phase)
                prev_phase = phase
                continue

            # Now figure out what to do with micro phases.
            prev_phase_slope = prev_phase.kslope if prev_phase is not None else inf
            prev_phase_flatter = abs(prev_phase_slope) < abs(next_phase.kslope)
            prev_phase_higher = prev_phase and prev_phase.end_value > next_phase.end_value

            # If no previous, just merge with next phase
            if not prev_phase:
                merge_on_next_loop = True
            # If flat, merge with whichever neighbor is flatter
            elif phase.trending == 'flat':
                if prev_phase_flatter:
                    merge_with_prev = True
                else:
                    merge_on_next_loop = True
            # If next phase is higher than previous, merge with next since this should extend trend
            elif phase.trending == 'rising':
                if prev_phase.trending == 'rising':
                    merge_with_prev = True
                # FIXME? Comment above and this line seem inconsistent.
                elif not prev_phase_higher:
                    merge_on_next_loop = True
                else:
                    merge_with_prev = True
            # Same logic as rising reversed
            else:  # phase.trending == 'falling'
                if prev_phase.trending == 'falling':
                    merge_with_prev = True
                elif prev_phase_higher:
                    merge_on_next_loop = True
                else:
                    merge_with_prev = True

            # Merge with previous if flagged above
            if merge_with_prev:
                phase = phase.merge(prev_phase)
                if prev_phase in merged_phases:
                    merged_phases.pop()

            if not merge_on_next_loop:
                merged_phases.append(phase)

            # on to next loop
            prev_phase = phase

        # Don't forget last phase
        merged_phases.append(phases[-1])
        return merged_phases

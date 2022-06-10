from config.app import WAVE_ANALYSIS_CONFIG


class WavePhase:
    def __init__(self, start_window, epidemic, **opts):
        self.windows = [start_window]
        self.epidemic = epidemic

        c = WAVE_ANALYSIS_CONFIG
        self.flat_slope_threshold = opts.get('flat_slope_threshold', c['flat_slope_threshold'])
        self.min_phase_size = opts.get('min_phase_size', c['min_phase_size'])

        self.end_window = None

    @property
    def started_on(self):
        return self.start_window.date

    @property
    def ended_on(self):
        if self.is_ended():
            return self.end_window.date

    @property
    def start_window(self):
        return self.windows[0]

    @property
    def last_window(self):
        return self.windows[-1]

    @property
    def start_value(self):
        return self.start_window.value

    @property
    def end_value(self):
        if self.is_ended():
            return self.end_window.value

    @property
    def last_value(self):
        return self.last_window.value

    @property
    def days(self):
        if not self.is_ended():
            return None
        return (self.ended_on - self.started_on).days

    @property
    def value_diff(self):
        return self.last_value - self.start_value

    @property
    def slope(self):
        return self.value_diff / self.days

    @property
    def kslope(self):
        # kilo-slope
        return self.slope * 1000

    @property
    def trend(self):
        if self.slope is None:
            return None

        if self.slope > self.flat_slope_threshold:
            return 1
        elif self.slope < -self.flat_slope_threshold:
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
    def add_window(self, window):
        self.windows.append(window)

    def merge(self, other_phase):
        start_phase = self if self.started_on < other_phase.started_on else other_phase
        end_phase = self if start_phase != self else other_phase
        merged_phase = WavePhase(start_phase.start_window, self.epidemic)
        merged_phase.windows = start_phase.windows + end_phase.windows[:-1]
        merged_phase.end(end_phase.end_window)
        return merged_phase

    def end(self, window):
        self.windows.append(window)
        self.end_window = window

    def is_ended(self):
        return self.end_window is not None

    def is_micro(self):
        if not self.is_ended():
            return None

        if self.days <= self.min_phase_size:
            return True

        return False

    def is_rising(self):
        return self.trending == 'rising'

    def is_falling(self):
        return self.trending == 'falling'

    def is_flat(self):
        return self.trending == 'flat'

    def get_timeline(self, key):
        return self.extract_timeline(self.epidemic.timelines[key])

    def extract_timeline(self, time_series):
        """Extract timeline for time series datapoints falling within range of this
        wave.
        """
        wave_timeline = {}

        for dated, value in sorted(time_series.items()):
            if dated > self.ended_on:
                return wave_timeline

            if dated >= self.started_on:
                wave_timeline[dated] = value

        return wave_timeline

    def __repr__(self):
        f = '<Phase start={} end={} days={} kslope={} trending={} micro?={}>'
        kslope = None if self.kslope is None else round(self.kslope, 1)
        return f.format(self.started_on, self.ended_on, self.days, kslope, self.trending,
                        self.is_micro())

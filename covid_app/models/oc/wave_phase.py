from config.app import WAVE_ANALYSIS_CONFIG


class WavePhase:
    def __init__(self, start_window, **opts):
        self.start_window = start_window
        self.end_window = None
        self.flat_slope_threshold = opts.get('flat_slope_threshold',
                                             WAVE_ANALYSIS_CONFIG['flat_slope_threshold'])
        self.min_phase_size = opts.get('min_phase_size',
                                       WAVE_ANALYSIS_CONFIG['min_phase_size'])

    @property
    def started_on(self):
        return self.start_window.date

    @property
    def ended_on(self):
        if self.is_ended:
            return self.end_window.date

    @property
    def start_value(self):
        return self.start_window.value

    @property
    def end_value(self):
        if self.is_ended:
            return self.end_window.value

    @property
    def is_ended(self):
        return self.end_window is not None

    @property
    def days(self):
        if not self.is_ended:
            return None
        return (self.ended_on - self.started_on).days

    @property
    def value_diff(self):
        if not self.is_ended:
            return None
        return self.end_value - self.start_value

    @property
    def kslope(self):
        if not self.is_ended:
            return None
        return self.value_diff / self.days * 100

    @property
    def trend(self):
        if self.kslope is None:
            return None

        if self.kslope > self.flat_slope_threshold:
            return 1
        elif self.kslope < -self.flat_slope_threshold:
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
    def merge(self, other_phase):
        start_phase = self if self.started_on < other_phase.started_on else other_phase
        end_phase = self if start_phase != self else other_phase
        merged_phase = WavePhase(start_phase.start_window)
        merged_phase.end(end_phase.end_window)
        return merged_phase

    def end(self, window):
        self.end_window = window

    def is_micro(self):
        if not self.is_ended:
            return None

        if self.days <= self.min_phase_size:
            return True

        return False

    def __repr__(self):
        f = '<Phase start={} end={} days={} kslope={} trending={} micro?={}>'
        kslope = None if self.kslope is None else round(self.kslope, 1)
        return f.format(self.started_on, self.ended_on, self.days, kslope, self.trending,
                        self.is_micro())
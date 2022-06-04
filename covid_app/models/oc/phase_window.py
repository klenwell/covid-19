import statistics
from math import floor

from config.app import WAVE_ANALYSIS_CONFIG


class PhaseWindow:
    def __init__(self, dated, values, **opts):
        self.date = dated
        self.values = values
        self.value = values[floor(len(values) / 2)]

        c = WAVE_ANALYSIS_CONFIG
        self.flat_slope_threshold = opts.get('flat_slope_threshold', c['flat_slope_threshold'])

    @property
    def value_change(self):
        return self.end_value - self.start_value

    @property
    def slope(self):
        return self.value_change / len(self.values)

    @property
    def kslope(self):
        return self.slope * 100

    @property
    def stdev(self):
        return statistics.stdev(self.values)

    @property
    def mean(self):
        return statistics.mean(self.values)

    @property
    def trend(self):
        if self.kslope > self.flat_slope_threshold:
            return 1
        elif self.kslope < -self.flat_slope_threshold:
            return -1
        else:
            return 0

    @property
    def start_value(self):
        return self.values[0]

    @property
    def end_value(self):
        return self.values[-1]

    def __repr__(self):
        f = '<PhaseWindow middate={} days={} kslope={:.1f} stdev={:.3f} trend={}>'
        return f.format(self.date, len(self.values), self.kslope, self.stdev, self.trend)

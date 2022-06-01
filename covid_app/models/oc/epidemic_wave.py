"""
EpidemicWave

A wave or lull in the infections during an epidemic.

A wave consists of a rise phases and a fall phase followed by a flat or rise phases.
A lull consists of a flat phase followed by a rise phase.
"""
from functools import cached_property


class EpidemicWave:
    def __init__(self, phases, time_series):
        self.phases = phases
        self.time_series = self.extract_wave_time_series(time_series)

    #
    # Properties
    #
    @property
    def start_phase(self):
        return self.phases[0]

    @property
    def end_phase(self):
        return self.phases[-1]

    @property
    def started_on(self):
        return self.start_phase.started_on

    @property
    def ended_on(self):
        return self.end_phase.ended_on

    @cached_property
    def dates(self):
        return sorted(self.time_series.keys())

    @property
    def days(self):
        return (self.ended_on - self.started_on).days

    #
    # Methods
    #
    def is_lull(self):
        return self.start_phase.is_flat()

    def is_wave(self):
        return self.start_phase.is_rising()

    def is_active(self):
        return self.start_phase.is_rising() and not self.end_phases.is_falling()

    def extract_wave_time_series(self, time_series):
        wave_time_series = {}

        for dated, value in sorted(time_series.items()):
            if dated > self.ended_on:
                return wave_time_series

            if dated >= self.started_on:
                wave_time_series[dated] = value

        return wave_time_series

    def __repr__(self):
        f = '<Epidemic{} start={} end={} days={}>'
        label = 'Wave' if self.is_wave() else 'Lull'
        return f.format(label, self.started_on, self.ended_on, self.days)

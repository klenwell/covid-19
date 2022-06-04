"""
EpidemicWave

A wave or lull in the infections during an epidemic.

A wave consists of a rise phases and a fall phase followed by a flat or rise phases.
A lull consists of a flat phase followed by a rise phase.
"""
from functools import cached_property


class EpidemicWave:
    def __init__(self, phases, epidemic):
        self.phases = phases
        self.epidemic = epidemic
        self.timeline = self.extract_timeline(epidemic.timeline)

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
        return sorted(self.timeline.keys())

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
        f = '<Epidemic{} start={} end={} days={}>'
        label = 'Wave' if self.is_wave() else 'Lull'
        return f.format(label, self.started_on, self.ended_on, self.days)

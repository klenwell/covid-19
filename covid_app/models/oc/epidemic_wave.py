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
        self.timeline = epidemic.extract_timeline_by_start_end_dates(
            epidemic.timeline,
            self.started_on,
            self.ended_on
        )
        self.timelines = {
            'primary': self.timeline
        }

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

    @property
    def peaked_on(self):
        for dated, value in self.timeline.items():
            if value == self.peak_value:
                return dated

    @property
    def peak_value(self):
        return max(self.timeline.values())

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
        return self.epidemic.extract_timeline_by_start_end_dates(
            self.epidemic.timelines[key],
            self.started_on,
            self.ended_on
        )

    def __repr__(self):
        f = '<Epidemic{} start={} end={} days={}>'
        label = 'Wave' if self.is_wave() else 'Lull'
        return f.format(label, self.started_on, self.ended_on, self.days)

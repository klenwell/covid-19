from datetime import datetime


class CovidVirusTest:
    #
    # Static Methods
    #
    @staticmethod
    def from_hsa():
        pass

    #
    # Properties
    #
    @property
    def administered_on(self):
        return datetime.utcfromtimestamp(self.administered_at/1000).date()

    @property
    def reported_on(self):
        return datetime.utcfromtimestamp(self.reported_at/1000).date()

    @property
    def days_to_result(self):
        return (self.reported_on - self.administered_on).days

    #
    # Instance Method
    #
    def __init__(self, **fields):
        self.reported_at = fields.get('repo_timestamp')
        self.administered_at = fields.get('spec_timestamp')
        self.result = fields.get('result')

    def __repr__(self):
        f = '<ColdVirusTest administered={} reported={} result={} days={}>'
        return f.format(self.administered_on, self.reported_on, self.result, self.days_to_result)

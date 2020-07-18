from datetime import datetime


class CovidVirusTest:
    #
    # Properties
    #
    @property
    def administered_on(self):
        if not self.administered_at:
            return None
        return datetime.utcfromtimestamp(self.administered_at/1000).date()

    @property
    def reported_on(self):
        if not self.reported_at:
            return None
        return datetime.utcfromtimestamp(self.reported_at/1000).date()

    @property
    def days_to_report(self):
        if not (self.reported_on and self.administered_on):
            return None
        return (self.reported_on - self.administered_on).days

    #
    # Instance Method
    #
    def __init__(self, **fields):
        self.reported_at = fields.get('reported_at')
        self.administered_at = fields.get('administered_at')
        self.result = fields.get('result')

    def __repr__(self):
        f = '<CovidVirusTest administered={} reported={} result={} days={}>'
        return f.format(self.administered_on, self.reported_on, self.result, self.days_to_result)

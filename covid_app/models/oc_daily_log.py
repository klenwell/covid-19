from os.path import join as path_join
from datetime import datetime
import csv

from config.app import DATA_ROOT


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')


class OcDailyLog:
    #
    # Static Methods
    #
    @staticmethod
    def all():
        collection = []
        csv_path = path_join(OC_DATA_PATH, 'oc-hca.csv')

        with open(csv_path, newline='') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Skip header
            next(csv_reader)

            for row in csv_reader:
                daily_log = OcDailyLog.from_export_row(row)
                collection.append(daily_log)

        return sorted(collection, key=lambda dl: dl.created_on)

    @staticmethod
    def from_export_row(row):
        int_or_none = lambda v: int(v) if v != '' else None
        float_or_none = lambda v: float(v) if v != '' else None
        created_on = datetime.strptime(row[0], '%Y-%m-%d').date()
        return OcDailyLog(created_on=created_on,
                          cases=int_or_none(row[1]),
                          tests=int_or_none(row[2]),
                          hospitalizations=int_or_none(row[3]),
                          icu_cases=int_or_none(row[4]),
                          deaths=int_or_none(row[5]),
                          rt=float_or_none(row[6]))

    #
    # Properties
    #
    @property
    def effective_reproduction_number(self):
        return '{:.2f}'.format(self.rt)

    @property
    def day_of_week(self):
        """Returns Sunday, Monday, etc, or Saturday.
        """
        if not self.created_on:
            return None

        return self.created_on.strftime('%A')

    #
    # Instance Method
    #
    def __init__(self, **fields):
        self.tests = fields.get('tests')
        self.cases = fields.get('cases')
        self.hospitalizations = fields.get('hospitalizations'),
        self.icu_cases = fields.get('icu_cases')
        self.deaths = fields.get('deaths')
        self.rt = fields.get('rt')
        self.created_on = fields.get('created_on')

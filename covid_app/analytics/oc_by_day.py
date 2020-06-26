from os.path import join as path_join
import csv
from statistics import mean, stdev

from config.app import DATA_ROOT
from covid_app.models.oc_daily_log import OcDailyLog


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')


class OcByDayAnalysis:
    def __init__(self):
        self.logs_by_day = {}
        self.headers = ['Day', 'Count',
                        'Tests', 'Tests μ', 'Tests σ',
                        'Cases', 'Cases μ', 'Cases σ']

    #
    # Properties
    #
    @property
    def days(self):
        return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    #
    # Instance Method
    #
    def analyze_dates(self, start_on, end_on):
        logs = OcDailyLog.all()

        for log in logs:
            if log.created_on < start_on or log.created_on > end_on:
                continue

            day_group = self.logs_by_day.get(log.day_of_week, [])
            day_group.append(log)
            self.logs_by_day[log.day_of_week] = day_group

        return self.logs_by_day

    def cases_by_day(self, day):
        return [log.cases for log in self.logs_by_day[day]]

    def tests_by_day(self, day):
        return [log.tests for log in self.logs_by_day[day]]

    def data_by_day(self, day):
        return {
            'day': day,
            'count': len(self.logs_by_day[day]),
            'cases': sum(self.cases_by_day(day)),
            'cases-mean': mean(self.cases_by_day(day)),
            'cases-stdev': stdev(self.cases_by_day(day)),
            'tests': sum(self.tests_by_day(day)),
            'tests-mean': mean(self.tests_by_day(day)),
            'tests-stdev': stdev(self.tests_by_day(day))
        }

    def data_to_csv_row(self, day):
        return [
            self.data_by_day(day)['day'],
            self.data_by_day(day)['count'],
            self.data_by_day(day)['tests'],
            self.data_by_day(day)['tests-mean'],
            self.data_by_day(day)['tests-stdev'],
            self.data_by_day(day)['cases'],
            self.data_by_day(day)['cases-mean'],
            self.data_by_day(day)['cases-stdev']
        ]

    def to_csv(self):
        pass

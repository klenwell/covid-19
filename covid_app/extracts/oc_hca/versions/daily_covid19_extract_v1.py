import json
from datetime import datetime
from functools import cached_property


class DailyCovid19ExtractV1:
    VERSION = 1
    ACTIVE_DATE = '2020-03-31'
    SERVICE_DATE_F = '%m/%d/%Y'
    START_DATE = '3/1/2020'

    #
    # Static Methods
    #
    def is_detected(html):
        needle = 'caseArr = [['
        return needle in html

    #
    # Instance Methods
    #
    def __init__(self, html):
        self.html = html

    @cached_property
    def new_cases(self):
        needle = 'caseArr ='
        count_idx = 1
        return self.extract_from_embedded_json_list(needle, count_idx)

    @cached_property
    def new_tests(self):
        needle = 'testData ='
        count_idx = 2
        return self.extract_from_embedded_json_list(needle, count_idx)

    @cached_property
    def hospitalizations(self):
        needle = 'hospitalArr ='
        count_idx = 1
        return self.extract_from_embedded_json_list(needle, count_idx)

    @cached_property
    def icu_cases(self):
        needle = 'hospitalArr ='
        count_idx = 2
        return self.extract_from_embedded_json_list(needle, count_idx)

    @property
    def dates(self):
        return sorted(self.new_cases)

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    def to_rows(self):
        rows = []

        for date in self.dates:
            row = (date, self.new_cases, self.new_tests, self.hospitalizations, self.icu_cases)
            rows.append(row)

        return rows

    #
    # Private
    #
    def extract_from_embedded_json_list(self, needle, idx):
        daily_values = {}

        _, tail = self.html.split(needle)
        payload, _ = tail.split(';', 1)
        daily_rows = json.loads(payload)

        for row in daily_rows:
            date = datetime.strptime(row[0], self.SERVICE_DATE_F).date()
            value = row[idx]
            daily_values[date] = value

        return daily_values

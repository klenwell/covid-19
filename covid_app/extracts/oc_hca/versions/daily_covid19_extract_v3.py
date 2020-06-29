import requests
from functools import cached_property
from datetime import datetime, date


EXTRACT_URL = ('https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/'
               'occovid_main_csv/FeatureServer/0/query?where=0%3D0&objectIds=&time=&resultType=none'
               '&outFields=date%2Cdaily_tests%2Cdaily_cases%2Cdaily_dth%2Cdaily_hosp%2Cdaily_icu'
               '&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false'
               '&returnDistinctValues=false&cacheHint=false'
               '&orderByFields=date'
               '&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset='
               '&resultRecordCount=&sqlFormat=none&f=pjson&token=')
TEST_DATA_URL = ("https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/"
                 "occovid_testing_csv"
                 "/FeatureServer/0/query?"
                 "where=daily_test_repo+IS+NOT+NULL"
                 "&objectIds=&time=&resultType=none&outFields=*"
                 "&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false"
                 "&returnDistinctValues=false&cacheHint=false&orderByFields=date&"
                 "groupByFieldsForStatistics=&outStatistics=&having=&resultOffset="
                 "&resultRecordCount=&sqlFormat=none&f=pjson&token=")


class DailyCovid19ExtractV3:
    VERSION = 3
    ACTIVE_DATE = '2020-06-26'

    #
    # Static Methods
    #
    def is_detected():
        try:
            tell = 'features'
            json_data = DailyCovid19ExtractV3.get_json_data()
            return tell in json_data.keys()
        except Exception:
            return False

    def get_json_data():
        response = requests.get(EXTRACT_URL)
        response.raise_for_status()
        return response.json()

    #
    # Properties
    #
    @cached_property
    def daily_logs(self):
        json_data = DailyCovid19ExtractV3.get_json_data()
        daily_logs = self.extract_from_json_data(json_data)
        return self.exclude_future_dates(daily_logs)

    @cached_property
    def daily_test_logs(self):
        response = requests.get(TEST_DATA_URL)
        response.raise_for_status()
        json_data = response.json()
        return self.extract_from_json_data(json_data)

    @cached_property
    def new_cases(self):
        key = 'daily_cases'
        return self.extract_from_daily_logs(key)

    @cached_property
    def new_tests(self):
        key = 'daily_test_repo'
        daily_logs = self.daily_test_logs
        return self.extract_from_logs(daily_logs, key)

    @cached_property
    def hospitalizations(self):
        key = 'daily_hosp'
        return self.extract_from_daily_logs(key)

    @cached_property
    def icu_cases(self):
        key = 'daily_icu'
        return self.extract_from_daily_logs(key)

    @cached_property
    def new_deaths(self):
        key = 'daily_dth'
        return self.extract_from_daily_logs(key)

    @property
    def dates(self):
        log_dates = []

        for daily_log in self.daily_logs:
            log_date = self.timestamp_to_date(daily_log['date'])
            log_dates.append(log_date)

        return sorted(log_dates)

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    #
    # Instance Methods
    #
    def __init__(self, html=None):
        pass

    def by_date(self, dated):
        return {
            'date': str(dated),
            'cases': self.new_cases.get(dated),
            'tests': self.new_tests.get(dated),
            'hospitalizations': self.hospitalizations.get(dated),
            'icu_cases': self.icu_cases.get(dated),
            'deaths': self.new_deaths.get(dated)
        }

    #
    # Private
    #
    def extract_from_json_data(self, json_data):
        features = json_data['features']
        data = [f['attributes'] for f in features if f.get('attributes')]
        return data

    def extract_from_daily_logs(self, key):
        daily_values = {}

        for daily_log in self.daily_logs:
            log_date = self.timestamp_to_date(daily_log['date'])
            value = daily_log[key]
            daily_values[log_date] = value

        return daily_values

    def extract_from_logs(self, logs, key):
        daily_values = {}

        for daily_log in logs:
            log_date = self.timestamp_to_date(daily_log['date'])
            value = daily_log[key]
            daily_values[log_date] = value

        return daily_values

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

    def exclude_future_dates(self, daily_logs):
        filtered_logs = []
        today = date.today()

        for daily_log in daily_logs:
            log_date = self.timestamp_to_date(daily_log['date'])
            if log_date <= today:
                filtered_logs.append(daily_log)

        return filtered_logs

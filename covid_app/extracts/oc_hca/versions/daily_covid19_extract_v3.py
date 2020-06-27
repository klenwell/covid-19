import requests
from functools import cached_property
from datetime import datetime


EXTRACT_URL = ('https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/'
               'occovid_main_csv/FeatureServer/0/query?where=0%3D0&objectIds=&time=&resultType=none'
               '&outFields=date%2Cdaily_tests%2Cdaily_cases%2Cdaily_dth%2Cdaily_hosp%2Cdaily_icu'
               '&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false'
               '&returnDistinctValues=false&cacheHint=false'
               '&orderByFields=date'
               '&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset='
               '&resultRecordCount=&sqlFormat=none&f=pjson&token=')


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
    # Instance Methods
    #
    def __init__(self, html=None):
        json_data = DailyCovid19ExtractV3.get_json_data()
        daily_logs = self.extract_from_json_data(json_data)
        self.daily_logs = self.filter_future_dates(daily_logs)

    @cached_property
    def new_cases(self):
        key = 'daily_cases'
        return self.extract_from_daily_logs(key)

    @cached_property
    def new_tests(self):
        key = 'daily_tests'
        return self.extract_from_daily_logs(key)

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
            date = self.timestamp_to_date(daily_log['date'])
            value = daily_log[key]
            daily_values[date] = value

        return daily_values

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

    def filter_future_dates(self, daily_logs):
        return daily_logs

import requests
from functools import cached_property
from datetime import datetime


EXTRACT_URL = 'https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services'
EXTRACT_URL_F = ("{}/{}/FeatureServer/0/query?where={}+IS+NOT+NULL"
                 "&objectIds=&time=&resultType=none&outFields=*"
                 "&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false"
                 "&returnDistinctValues=false&cacheHint=false&orderByFields=date&"
                 "groupByFieldsForStatistics=&outStatistics=&having=&resultOffset="
                 "&resultRecordCount=&sqlFormat=none&f=pjson&token=")


class DailyCovid19ExtractV3:
    VERSION = 3.3
    ACTIVE_DATE = '2020-07-15'

    #
    # Static Methods
    #
    def is_detected():
        tell = 'features'
        url = EXTRACT_URL_F.format(EXTRACT_URL, 'occovid_main_csv', 'daily_cases')

        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            return tell in json_data.keys()
        except Exception:
            return False

    #
    # Properties
    #
    @cached_property
    def daily_case_logs(self):
        endpoint = 'occovid_case_csv'
        where_not_null_field = 'daily_cases_repo'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def daily_test_logs(self):
        endpoint = 'occovid_pcr_csv'
        where_not_null_field = 'daily_test_repo'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def daily_hospitalization_logs(self):
        endpoint = 'occovid_hospicu_csv'
        where_not_null_field = 'hospital'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def daily_death_logs(self):
        endpoint = 'occovid_death_csv'
        where_not_null_field = 'daily_dth'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def new_cases(self):
        key = 'daily_cases_repo'
        daily_logs = self.daily_case_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_tests(self):
        key = 'daily_test_repo'
        daily_logs = self.daily_test_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def hospitalizations(self):
        key = 'hospital'
        daily_logs = self.daily_hospitalization_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def icu_cases(self):
        key = 'icu'
        daily_logs = self.daily_hospitalization_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_deaths(self):
        key = 'daily_dth'
        daily_logs = self.daily_death_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @property
    def dates(self):
        return sorted(self.new_cases.keys())

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    #
    # Instance Methods
    #
    def __init__(self):
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
    def fetch_json_data(self, endpoint, where_not_null_field):
        url = EXTRACT_URL_F.format(EXTRACT_URL, endpoint, where_not_null_field)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def extract_from_json_data(self, json_data):
        features = json_data['features']
        data = [f['attributes'] for f in features if f.get('attributes')]
        return data

    def extract_from_daily_logs(self, daily_logs, key):
        daily_values = {}

        # Normalize the timestamp key. In cases feed, it's "Date", in tests feed "date".
        if 'Date' in daily_logs[0]:
            timestamp_key = 'Date'
        else:
            timestamp_key = 'date'

        for daily_log in daily_logs:
            timestamp = daily_log[timestamp_key]
            log_date = self.timestamp_to_date(timestamp)
            value = daily_log[key]
            daily_values[log_date] = value

        return daily_values

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

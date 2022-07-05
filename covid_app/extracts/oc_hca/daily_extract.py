"""
OC Health Care Agency Data

For info on data source, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services
"""
import requests
import urllib.parse
import json
from os.path import join as path_join
from functools import cached_property
from datetime import datetime, timedelta

from config.app import DATA_ROOT


# URL parts for HCA data API
API_ID = 'LORzk2hk9xzHouw9'
API_DOMAIN = 'https://services2.arcgis.com'
API_URL_F = '{}/{}/ArcGIS/rest/services/{}/FeatureServer/0/query'


class DataSourceError(Exception):
    pass


class OcHcaDailyExtract:
    #
    # Properties
    #
    # Data Source Info
    @property
    def query_params(self):
        return {
            'where': '{}+IS+NOT+NULL',
            'orderByFields': 'date',
            'f': 'pjson',
            'objectIds': '',
            'outFields': '*',
            'time': '',
            'resultType': 'none',
            'returnIdsOnly': 'false',
            'returnUniqueIdsOnly': 'false',
            'returnCountOnly': 'false',
            'returnDistinctValues': 'false',
            'cacheHint': 'false',
            'groupByFieldsForStatistics': '',
            'outStatistics': '',
            'having': '',
            'resultOffset': '',
            'resultRecordCount': '',
            'sqlFormat': 'none',
            'token': '',
        }

    # Data Extracts
    @cached_property
    def daily_case_time_series(self):
        endpoint = 'occovid_case_csv'
        where_not_null_field = 'daily_cases_repo'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def daily_test_time_series(self):
        endpoint = 'occovid_pcr_csv'
        where_not_null_field = 'daily_test_repo'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def daily_hospitalization_time_series(self):
        endpoint = 'occovid_hospicu_csv'
        where_not_null_field = 'hospital'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def daily_death_time_series(self):
        endpoint = 'occovid_death_csv'
        where_not_null_field = 'daily_dth'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    # Data Series (mapped to dates)
    @cached_property
    def new_cases(self):
        key = 'daily_cases_repo'
        time_series = self.daily_case_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def new_tests_reported(self):
        key = 'daily_test_repo'
        time_series = self.daily_test_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def new_tests_administered(self):
        key = 'daily_spec'
        time_series = self.daily_test_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def new_positive_tests_administered(self):
        key = 'daily_pos_spec'
        time_series = self.daily_test_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def hospitalizations(self):
        key = 'hospital'
        time_series = self.daily_hospitalization_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def icu_cases(self):
        key = 'icu'
        time_series = self.daily_hospitalization_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def total_snf_cases(self):
        # SNF refers to Skilled Nursing Facilities
        key = 'snf_cases'
        time_series = self.daily_case_time_series
        return self.extract_from_time_series(time_series, key)

    @cached_property
    def new_snf_cases(self):
        daily_snf_cases = {}
        dates = sorted(self.total_snf_cases.keys())

        for dated in dates:
            snf_cases = self.total_snf_cases.get(dated)
            last_snf_cases_report = self.get_previous_total_snf_cases(dated)

            if snf_cases is None:
                snf_cases = 0

            if last_snf_cases_report is None:
                last_snf_cases_report = 0

            daily_snf_cases[dated] = snf_cases - last_snf_cases_report

        return daily_snf_cases

    @cached_property
    def new_deaths(self):
        key = 'daily_dth'
        time_series = self.daily_death_time_series
        return self.extract_from_time_series(time_series, key)

    # Dates
    @property
    def dates(self):
        dates = []

        # Fencepost alert: Don't forget to add one to range to include final day.
        for n in range(int((self.ends_on - self.starts_on).days) + 1):
            date = self.starts_on + timedelta(n)
            dates.append(date)
        return dates

    @property
    def new_case_dates(self):
        return sorted(self.new_cases.keys())

    @property
    def starts_on(self):
        return self.new_case_dates[0]

    @property
    def ends_on(self):
        return self.new_case_dates[-1]

    #
    # Instance Methods
    #
    def __init__(self, mock=False):
        self.fetch_samples = mock

    def mock_api_calls(self):
        self.fetch_samples = True

    #
    # Private
    #
    def build_endpoint_url(self, endpoint):
        return API_URL_F.format(API_DOMAIN, API_ID, endpoint)

    def build_query_params(self, where_not_null_field):
        # Source: https://stackoverflow.com/a/23497912/1093087
        query_params = self.query_params.copy()
        query_params['where'] = query_params['where'].format(where_not_null_field)
        return urllib.parse.urlencode(query_params, safe=':+*')

    def fetch_json_data(self, endpoint, where_not_null_field):
        url = self.build_endpoint_url(endpoint)
        query_params = self.build_query_params(where_not_null_field)

        if self.fetch_samples:
            sample_file_name = 'oc-hca-{}.json'.format(endpoint)
            json_path = path_join(DATA_ROOT, 'samples', sample_file_name)
            print('fetching mock data from {}'.format(json_path))

            with open(json_path) as f:
                return json.load(f)
        else:
            response = requests.get(url, params=query_params)
            response.raise_for_status()
            return response.json()

    def extract_from_json_data(self, json_data):
        features = json_data['features']
        data = [f['attributes'] for f in features if f.get('attributes')]
        return data

    def extract_from_time_series(self, time_series, key):
        daily_values = {}

        # Normalize the timestamp key. In cases feed, it's "Date", in tests feed "date".
        if 'Date' in time_series[0]:
            timestamp_key = 'Date'
        else:
            timestamp_key = 'date'

        for daily_data in time_series:
            timestamp = daily_data[timestamp_key]
            dated = self.timestamp_to_date(timestamp)
            value = daily_data[key]
            daily_values[dated] = value

        return daily_values

    def get_previous_total_snf_cases(self, dated):
        # Look up to a week in past in case there were missing date reports.
        week_ago = 8

        for ago in range(1, week_ago):
            previous_date = dated - timedelta(days=ago)
            cases = self.total_snf_cases.get(previous_date)
            if cases:
                return cases

        return None

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

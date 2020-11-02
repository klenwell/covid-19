"""
San Diego County COVID-19 Data

For info on data source, see:
https://services1.arcgis.com/1vIhDJwtG5eNmiqX/ArcGIS/rest/services
"""
import requests
from functools import cached_property
from datetime import datetime, timedelta
from collections import deque
import csv


EXTRACT_URL = 'https://services1.arcgis.com/1vIhDJwtG5eNmiqX/ArcGIS/rest/services'
EXTRACT_URL_F = ("{}/{}/FeatureServer/1/query?where={}+IS+NOT+NULL"
                 "&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR="
                 "&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0"
                 "&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*"
                 "&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint"
                 "&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation="
                 "&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false"
                 "&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false"
                 "&returnDistinctValues=false&cacheHint=false&orderByFields=Date"
                 "&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset="
                 "&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true"
                 "&quantizationParameters=&sqlFormat=none&f=pjson&token=")

# Source: https://www.cdc.gov/coronavirus/2019-ncov/hcp/clinical-guidance-management-patients.html
MEDIAN_LENGTH_OF_HOSPITALIZATION = 10

# Source: https://www.cbc.ca/news/health/typical-covid-19-progression-1.5546949
MEDIAN_LENGTH_OF_ICU_STAY = 10

# Source: https://www.census.gov/quickfacts/fact/table/sandiegocountycalifornia,CA/PST045219
TOTAL_POPULATION = 3338330


class SanDiegoCountyDailyExtract:
    VERSION = 0.1

    #
    # Static Methods
    #
    def is_in_order():
        tell = 'features'
        url = EXTRACT_URL_F.format(EXTRACT_URL, 'CovidDashUpdate', 'NewCases')

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
    def daily_logs(self):
        endpoint = 'CovidDashUpdate'
        where_not_null_field = 'NewCases'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return self.extract_from_json_data(json_data)

    @cached_property
    def new_cases(self):
        key = 'NewCases'
        daily_logs = self.daily_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_tests_reported(self):
        key = 'NewTests'
        daily_logs = self.daily_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def total_positive_tests(self):
        key = 'Positives'
        daily_logs = self.daily_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_tests_administered(self):
        pass

    @cached_property
    def new_positive_tests_administered(self):
        pass

    @cached_property
    def total_hospitalizations(self):
        key = 'Hospitalized'
        daily_logs = self.daily_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_hospitalizations(self):
        return self.break_out_count_by_day(self.total_hospitalizations)

    @cached_property
    def estimated_hospitalizations(self):
        active_hospitalizations = {}
        hospital_queue = deque([0] * MEDIAN_LENGTH_OF_HOSPITALIZATION)

        for dated in self.dates:
            new_hospitalizations = self.new_hospitalizations.get(dated, 0)
            hospital_queue.pop()
            hospital_queue.appendleft(new_hospitalizations)
            active_hospitalizations[dated] = sum(hospital_queue)

        return active_hospitalizations

    @cached_property
    def total_icu_cases(self):
        key = 'ICU'
        daily_logs = self.daily_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_icu_cases(self):
        return self.break_out_count_by_day(self.total_icu_cases)

    @cached_property
    def estimated_icu_cases(self):
        active_icu_cases = {}
        icu_queue = deque([0] * MEDIAN_LENGTH_OF_ICU_STAY)

        for dated in self.dates:
            new_icu_cases = self.new_icu_cases.get(dated, 0)
            icu_queue.pop()
            icu_queue.appendleft(new_icu_cases)
            active_icu_cases[dated] = sum(icu_queue)

        return active_icu_cases

    @cached_property
    def total_deaths(self):
        key = 'Deaths'
        daily_logs = self.daily_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @cached_property
    def new_deaths(self):
        return self.break_out_count_by_day(self.total_deaths)

    @property
    def dates(self):
        return sorted(self.total_positive_tests.keys())

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    @property
    def csv_headers(self):
        return [
            'Date',
            'New Tests Reported',
            'New Cases',
            'New Hospitalizations',
            'Estimated Hospitalizations',
            'New ICU Cases',
            'Estimated ICU Cases',
            'New Deaths'
        ]

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    def to_csv(self, csv_path):
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.csv_headers)

            for dated in reversed(self.dates):
                writer.writerow(self.data_to_csv_row(dated))

        return csv_path

    def data_to_csv_row(self, dated):
        return [
            dated,
            self.new_tests_reported.get(dated),
            self.new_cases.get(dated),
            self.new_hospitalizations.get(dated),
            self.estimated_hospitalizations.get(dated),
            self.new_icu_cases.get(dated),
            self.estimated_icu_cases.get(dated),
            self.new_deaths.get(dated)
        ]

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
        timestamp_key = 'Date'

        for daily_log in daily_logs:
            timestamp = daily_log[timestamp_key]
            log_date = self.timestamp_to_date(timestamp)
            value = daily_log[key]
            daily_values[log_date] = value

        return daily_values

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

    def break_out_count_by_day(self, daily_totals):
        daily_count = {}
        dates = sorted(daily_totals.keys())

        for dated in dates:
            day_before = dated - timedelta(days=1)
            todays_total = daily_totals.get(dated)
            yesterdays_total = daily_totals.get(day_before)

            if todays_total is None:
                todays_total = 0

            if yesterdays_total is None:
                yesterdays_total = 0

            daily_count[dated] = todays_total - yesterdays_total

        return daily_count

"""
OC Health Care Agency Vaccines Extract

For info on data source, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services
"""
import requests
from functools import cached_property
from datetime import datetime, timedelta


EXTRACT_URL = 'https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services'
EXTRACT_URL_F = ("{}/{}/FeatureServer/0/query?where={}+IS+NOT+NULL"
                 "&objectIds=&time=&resultType=none&outFields=*"
                 "&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false"
                 "&returnDistinctValues=false&cacheHint=false&orderByFields="
                 "&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset="
                 "&resultRecordCount=&sqlFormat=none&f=pjson&token=")


class OCVaccinationsExtract:
    VERSION = 0.1

    #
    # Properties
    #
    @cached_property
    def daily_doses(self):
        key = 'valid_admin'
        daily_logs = self.daily_dose_logs
        return self.extract_from_daily_logs(daily_logs, key)

    @property
    def dose_dates(self):
        return sorted(self.daily_doses.keys())

    @property
    def starts_on(self):
        return self.dose_dates[0]

    @property
    def ends_on(self):
        return self.dose_dates[-1]

    @property
    def dates(self):
        dates = []

        # Fencepost alert: Don't forget to add one to range to include final day.
        for n in range(int((self.ends_on - self.starts_on).days) + 1):
            date = self.starts_on + timedelta(n)
            dates.append(date)
        return dates

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    #
    # Private
    #
    @cached_property
    def json_data(self):
        endpoint = 'vacc_dosebydate'
        where_not_null_field = 'valid_admin'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return json_data

    @cached_property
    def daily_dose_logs(self):
        return self.extract_from_json_data(self.json_data)

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
        timestamp_key = 'vac_date'

        for daily_log in daily_logs:
            timestamp = daily_log[timestamp_key]
            log_date = self.timestamp_to_date(timestamp)
            value = daily_log[key]
            daily_values[log_date] = value

        return daily_values

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

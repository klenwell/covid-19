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


class OCVaccinationsSummaryExtract:
    VERSION = 0.1

    #
    # Properties
    #
    @cached_property
    def categories(self):
        return self.rows_by_category.keys()

    @cached_property
    def rows_by_category(self):
        category_rows = {}

        for row in self.rows:
            category = row['category']
            category_rows[category] = row

        return category_rows

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    def by_category(self, category):
        return self.rows_by_category.get(category)

    #
    # Private
    #
    @cached_property
    def json_data(self):
        endpoint = 'vacc_totalsummary'
        where_not_null_field = 'category'
        json_data = self.fetch_json_data(endpoint, where_not_null_field)
        return json_data

    @cached_property
    def rows(self):
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

    def timestamp_to_date(self, timestamp):
        return datetime.utcfromtimestamp(timestamp/1000).date()

"""
Programmatically extracts Michigan Kent County COVID-19 data from US government API.
Testing data is available on MI website here:

https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html

The request data constants below may need to be updated from time to time. To retrieve
values, do the following:

1. In Firefox, go here: https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html
2. Click TOTAL TESTING tab in dashboard
3. Open Firefox console and go to Network tab. Click trashcan icon to clear log.
4. In County field, select Kent
5. Look for a POST request to the following URL, size will be ~12kb:
   https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true
6. Right click the item > Copy > Copy as cURL. This will provide the request header and body
   data for the API request.
7. Values for WABI constants below will be found in the --data-raw parameter.
"""
import requests
import json
from datetime import datetime
from functools import cached_property


#
# Constants
#
EXTRACT_URL = 'https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata'

# US Gov API request parameters
WABI_DATASET_ID = '68c49ce8-850a-41fb-8211-dcf5bd8a7281'
WABI_REPORT_ID = 'c6f0a0f7-5ac0-4279-bcc2-e47e9439674e'
WABI_MODEL_ID = '348880'


class UsGovCovid19Extract:
    #
    # Property
    #
    @property
    def request_headers(self):
        # headers were simply copy-pasted from Firefox console.
        headers = {
            'Host': 'wabi-us-gov-iowa-api.analysis.usgovcloudapi.net',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://app.powerbigov.us',
            'ActivityId': '0eb36de8-1e21-4344-9847-04d7077eef75',
            'RequestId': '09b0368c-2803-2e54-c4a7-08a458fb20b6',
            'X-PowerBI-ResourceKey': 'a4abbd9d-08f8-456e-b02b-f4c08be8888b',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://app.powerbigov.us',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        return headers

    @property
    def kent_request_data(self):
        data_str = (
            '{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":'
            '{"Query":{"Version":2,"From":[{"Name":"t1","Entity":"Testing_Data"},{"Name":"c",'
            '"Entity":"Cases by County"}],"Select":[{"Column":{"Expression":{"SourceRef":'
            '{"Source":"t1"}},"Property":"TestType"},"Name":"Testing_Data.TestType"},{"Column":'
            '{"Expression":{"SourceRef":{"Source":"t1"}},"Property":"MessageDate"},"Name":'
            '"Testing_Data.MessageDate"},{"Aggregation":{"Expression":{"Column":{"Expression":'
            '{"SourceRef":{"Source":"t1"}},"Property":"TestCount"}},"Function":0},"Name":'
            '"CountNonNull(Testing_Data.TestCount)"}],"Where":[{"Condition":{"In":{"Expressions":'
            '[{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"COUNTY"}}],'
            '"Values":[[{"Literal":{"Value":"\'Kent\'"}}]]}}}]},'
            '"Binding":{"Primary":{"Groupings":[{"Projections":[1,2]}]},"Secondary":{"Groupings":'
            '[{"Projections":[0]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}},'
            '"Secondary":{"Top":{}}},"Version":1}}}]},"QueryId":"","ApplicationContext":'
            '{"DatasetId":"%s","Sources":[{"ReportId":"%s"}]}}],"cancelQueries":[],"modelId":%s}'
        )
        raw_data = data_str % (WABI_DATASET_ID, WABI_REPORT_ID, WABI_MODEL_ID)

        # FIXME: I just copy-pasted this using steps outlined at top. This is the quick and
        # dirty way to pull test data. In future, figure out how to get this data civilly.
        raw_data = '{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"t","Entity":"Testing Data","Type":0},{"Name":"c","Entity":"Cases by County","Type":0}],"Select":[{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"t"}},"Property":"TestCount"}},"Function":0},"Name":"Sum(Testing Data.TestCount)"},{"Column":{"Expression":{"SourceRef":{"Source":"t"}},"Property":"MessageDate"},"Name":"Testing Data.MessageDate"},{"Column":{"Expression":{"SourceRef":{"Source":"t"}},"Property":"TestType"},"Name":"Testing Data.TestType"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"COUNTY"}}],"Values":[[{"Literal":{"Value":"\'Kent\'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"Secondary":{"Groupings":[{"Projections":[2]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}},"Secondary":{"Top":{}}},"Version":1},"ExecutionMetricsKind":1}}]},"QueryId":"","ApplicationContext":{"DatasetId":"68c49ce8-850a-41fb-8211-dcf5bd8a7281","Sources":[{"ReportId":"c6f0a0f7-5ac0-4279-bcc2-e47e9439674e","VisualId":"3bfd1db1633430448f1c"}]}}],"cancelQueries":[],"modelId":348880}'
        return json.loads(raw_data)

    @cached_property
    def daily_kent_json_data(self):
        return self.fetch_data_source(self.kent_request_data, self.request_headers)

    @property
    def daily_kent_logs(self):
        daily_logs = {}

        results_data = self.daily_kent_json_data['results'][0]['result']['data']
        daily_records = results_data['dsr']['DS'][0]['PH'][0]['DM0'][1:]

        for daily_record in daily_records:
            timestamp = daily_record['G0']
            dated = self.timestamp_to_date(timestamp)
            viral_test_count = daily_record['X'][0].get('M0')

            # Not sure why, but there are a number of records with this value:
            # {'G0': 1585785600000, 'X': [{'R': 1}]}
            # 1585785600000 => 2020-04-02
            if viral_test_count:
                daily_logs[dated] = viral_test_count

        return daily_logs

    @property
    def daily_kent_tests(self):
        daily_tests = {}

        for dated in self.kent_dates:
            daily_tests[dated] = self.daily_kent_logs.get(dated)

        return daily_tests

    @property
    def kent_dates(self):
        return sorted(self.daily_kent_logs.keys())

    #
    # Instance Methods
    #
    def __init__(self):
        self.url = EXTRACT_URL

    #
    # Private
    #
    def fetch_data_source(self, json_data, headers):
        response = requests.post(self.url, json=json_data, headers=headers)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        return response.json()

    def timestamp_to_date(self, ts):
        return datetime.utcfromtimestamp(ts/1000).date()

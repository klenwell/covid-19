import requests
import json
from datetime import datetime
from functools import cached_property


EXTRACT_URL = 'https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true'


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
            'Referer': 'https://app.powerbigov.us/view?r=eyJrIjoiNDY0ZGVlMDItMzUzNC00ZGE5LWFjYzQtNzliOGJkZWQ4YTgzIiwidCI6ImQ1ZmI3MDg3LTM3NzctNDJhZC05NjZhLTg5MmVmNDcyMjVkMSJ9',
            'ActivityId': '75b492ea-c96c-4e99-a956-5ab5fef9d1e6',
            'RequestId': 'ca0f3948-e675-198c-bcaa-0cdf77e0c15b',
            'X-PowerBI-ResourceKey': '464dee02-3534-4da9-acc4-79b8bded8a83',
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
            '{"DatasetId":"59638bad-f747-4eeb-9e60-02fdca2acfcd","Sources":[{"ReportId":'
            '"1e588afe-f0c7-4140-8350-e1212396c270"}]}}],"cancelQueries":[],"modelId":303803}'
        )
        return json.loads(data_str)

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

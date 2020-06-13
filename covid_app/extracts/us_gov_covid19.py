import requests
import json
from datetime import datetime


EXTRACT_URL = 'https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata'


class UsGovCovid19Extract:
    #
    # Static Methods
    #
    @staticmethod
    def kent_daily_tests():
        """Returns a dict: {date: count, ...} for Kent, MI.
        """
        # headers and body were simply copy-pasted from Firefox console.
        headers = {
            'Host': 'wabi-us-gov-iowa-api.analysis.usgovcloudapi.net',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https',
            'ActivityId': '34d568b0-c29e-4f30-9cf0-f04afd959aca',
            'RequestId': '8ea32a6f-d19c-c4b7-79b2-641759d959df',
            'X-PowerBI-ResourceKey': '1ccb55ad-71e0-47fe-8762-bd11b89b00f5',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https',
            'DNT': '1',
            'Connection': 'keep-alive'
        }

        body = (
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
            '{"DatasetId":"3538771d-70f8-4399-9760-267975e37f65","Sources":[{"ReportId":'
            '"f489615d-c09e-43f9-b6bb-db2832eb0e0d"}]}}],"cancelQueries":[],"modelId":282246}'
        )
        json_data = json.loads(body)

        extract = UsGovCovid19Extract()
        json_data = extract.fetch_data_source(json_data, headers)
        daily_tests_dict = extract.filter_kent_tests(json_data)
        return daily_tests_dict

    #
    # Instance Methods
    #
    def __init__(self):
        self.url = EXTRACT_URL

    def filter_kent_tests(self, json_data):
        """Returns a dict: {date: count, ...}
        """
        daily_values = {}

        # Microsoft BI data structuing
        gov_data = json_data['results'][0]['result']['data']
        test_data = gov_data['dsr']['DS'][0]['PH'][0]['DM0'][1:]

        daily_values = {}
        for td in test_data:
            ts = td['G0']
            date = datetime.utcfromtimestamp(ts/1000).date()
            viral_tests = td['X'][0]['M0']
            daily_values[date] = viral_tests

        return daily_values

    #
    # Private
    #
    def fetch_data_source(self, json_data, headers):
        response = requests.post(self.url, json=json_data, headers=headers)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        return response.json()

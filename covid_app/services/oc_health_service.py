"""
Orange County Health Service

Uses OC HCA API. For more information, see:

https://occovid19.ochealthinfo.com/coronavirus-in-oc
"""
from functools import cached_property
from datetime import datetime
import requests
import json


SERVICE_URL = 'https://occovid19.ochealthinfo.com/coronavirus-in-oc'


class OCHealthService:

    #
    # Instance Method
    #
    def __init__(self):
        self.url = SERVICE_URL
        self.html = self.fetch_page_source()

    def fetch_page_source(self):
        response = requests.get(self.url)

        # This will raise a requests.exceptions.HTTPError error for caller to handle.
        response.raise_for_status()

        return response.text

    def extract_new_tests(self):
        needle = 'testData ='
        date_f = '%m/%d/%Y'
        _, tail = self.html.split(needle)
        payload, _ = tail.split(';', 1)
        new_tests = json.loads(payload)
        return [(datetime.strptime(nt[0], date_f).date(), nt[2]) for nt in new_tests]

    def extract_new_cases(self):
        needle = 'caseArr ='
        date_f = '%m/%d/%Y'
        _, tail = self.html.split(needle)
        payload, _ = tail.split(';', 1)
        new_cases = json.loads(payload)
        return [(datetime.strptime(nc[0], date_f).date(), nc[1]) for nc in new_cases]

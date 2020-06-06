import requests

from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v1 import DailyCovid19ExtractV1
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v2 import DailyCovid19ExtractV2


EXTRACT_URL = 'https://occovid19.ochealthinfo.com/coronavirus-in-oc'
SERVICE_DATE_F = '%m/%d/%Y'
START_DATE = '3/1/2020'


class ExtractError(Exception):
    pass


class DailyCovid19Extract:
    #
    # Static Methods
    #
    def new():
        handler = DailyCovid19Extract(EXTRACT_URL)
        html = handler.fetch_data_source()
        ExtractVersion = handler.detect_version(html)
        return ExtractVersion(html)

    #
    # Instance Methods
    #
    def __init__(self, url=None):
        self.url = url if url else EXTRACT_URL

    def fetch_data_source(self):
        response = requests.get(self.url)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        return response.text

    def detect_version(self, html):
        if DailyCovid19ExtractV2.is_detected(html):
            return DailyCovid19ExtractV2
        elif DailyCovid19ExtractV1.is_detected(html):
            return DailyCovid19ExtractV1
        else:
            raise ExtractError('Valid extract source not detected.')

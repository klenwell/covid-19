"""
DailyCovid19Extract

This class is a handler for the class that does the actual extraction. Those classes
are versioned to simplify responding to updates or breakage in the underlying.

See versions directory, for latest version of class doing actual extraction.
"""
import requests

from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v1 import DailyCovid19ExtractV1
from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v2 import DailyCovid19ExtractV2


EXTRACT_URL = 'https://occovid19.ochealthinfo.com/coronavirus-in-oc'


class ExtractError(Exception):
    pass


class DailyCovid19Extract:
    #
    # Static Methods
    #
    def latest():
        handler = DailyCovid19Extract(EXTRACT_URL)
        html = handler.fetch_data_source()
        ExtractVersion = handler.detect_version(html)
        return ExtractVersion(html)

    def archive(url):
        handler = DailyCovid19Extract(url)
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

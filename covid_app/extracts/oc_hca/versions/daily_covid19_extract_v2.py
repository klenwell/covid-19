from covid_app.extracts.oc_hca.versions.daily_covid19_extract_v1 import DailyCovid19ExtractV1


class DailyCovid19ExtractV2(DailyCovid19ExtractV1):
    VERSION = 2
    ACTIVE_DATE = '2020-06-03'

    #
    # Static Methods
    #
    def is_detected(html):
        needle = '$cases = [['
        return needle in html

    #
    # Instance Methods
    #
    def __init__(self, html):
        super().__init__(html)

class DailyCovid19ExtractV1:
    VERSION = 1
    ACTIVE_DATE = '2020-03-31'

    #
    # Static Methods
    #
    def is_detected(html):
        needle = 'caseArr = [['
        return needle in html

    #
    # Instance Methods
    #
    def __init__(self, html):
        self.html = html

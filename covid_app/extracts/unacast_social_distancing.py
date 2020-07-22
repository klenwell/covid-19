import requests
from functools import cached_property
from datetime import datetime


EXTRACT_URL = 'https://covid19-scoreboard-api.unacastapis.com/api/search/covidcountyaggregates_v3'
EXTRACT_URL_F = "{}?q=countyFips:{}&size=4000"
FIPS_CODES = {
    'oc': '06059'
}


class UnacastSocialDistancingExtract:
    VERSION = '1.0'
    ACTIVE_DATE = '2020-07-20'

    #
    # Static Methods
    #
    def oc():
        fips_code = FIPS_CODES['oc']
        extract = UnacastSocialDistancingExtract(fips_code)
        return extract

    #
    # Properties
    #
    @cached_property
    def json_data(self):
        url = EXTRACT_URL_F.format(EXTRACT_URL, self.fips_code)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @cached_property
    def daily_logs(self):
        daily_logs = {}
        source_data = self.json_data['hits']['hits'][0]['_source']['data']

        for daily_data in source_data:
            date_str = daily_data['date']
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            daily_logs[log_date] = daily_data

        return daily_logs

    @property
    def state(self):
        return self.json_data['hits']['hits'][0]['_source']['stateName']

    @property
    def county(self):
        return self.json_data['hits']['hits'][0]['_source']['countyName']

    @property
    def population(self):
        return self.json_data['hits']['hits'][0]['_source']['population']

    @property
    def travel_distance_scores(self):
        key = 'travelDistanceMetric'
        return self.extract_from_daily_logs(key)

    @property
    def visitation_scores(self):
        key = 'visitationMetric'
        return self.extract_from_daily_logs(key)

    @property
    def encounter_densities(self):
        key = 'encountersMetric'
        return self.extract_from_daily_logs(key)

    @property
    def grades(self):
        key = 'totalGrade'
        return self.extract_from_daily_logs(key)

    @property
    def dates(self):
        return sorted(self.daily_logs.keys())

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    #
    # Instance Methods
    #
    def __init__(self, fips_code):
        self.fips_code = fips_code

    def by_date(self, dated):
        return {
            'date': str(dated),
            'travel-distance-score': self.travel_distance_scores.get(dated),
            'visitation-score': self.visitation_scores.get(dated),
            'encounter-density': self.encounter_densities.get(dated),
            'grade': self.grades.get(dated)
        }

    def pre_cache(self):
        # This method simply invokes a property that will fetch remote data.
        return self.daily_logs

    def fail_fast(self):
        # This should raise an Exception if there are issue with extract data source.
        self.pre_cache()
        return False    # i.e. no failure

    #
    # Private
    #
    def extract_from_daily_logs(self, key):
        daily_values = {}

        for dated, daily_data in self.daily_logs.items():
            value = daily_data.get(key)
            daily_values[dated] = value

        return daily_values

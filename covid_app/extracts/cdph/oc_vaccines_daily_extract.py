"""
CA Department of Health Vaccines Extract

For data source, see CDPH Data Portal:
https://data.ca.gov/dataset/covid-19-vaccine-progress-dashboard-data

The CDPH will occasionally update the resource ID (EXTRACT_ID below). For more info, see:
https://github.com/klenwell/covid-19/issues/82
"""
import requests
from functools import cached_property
from datetime import datetime, timedelta


EXTRACT_URL = 'https://data.ca.gov/api/3/action/datastore_search_sql'
EXTRACT_ID = 'eef88868-0cfc-4655-8a5a-3d1af1d23498'
EXTRACT_CO = 'Orange'
EXTRACT_URL_F = "{}?sql=SELECT%20*%20from%20%22{}%22%20WHERE%20%22county%22%20LIKE%20%27{}%27"
START_DATE = '2020-08-01'


class OcVaccinesDailyExtract:
    #
    # Properties
    #
    @property
    def url(self):
        return EXTRACT_URL_F.format(EXTRACT_URL, EXTRACT_ID, EXTRACT_CO)

    @cached_property
    def records(self):
        return self.json_data['result']['records']

    @cached_property
    def partially_vaccinated(self):
        key = 'partially_vaccinated'
        records = {}
        for date in self.dates:
            doses = self.extract_from_dated_records(key, date)
            records[date] = doses
        return records

    @cached_property
    def fully_vaccinated(self):
        key = 'fully_vaccinated'
        records = {}
        for date in self.dates:
            doses = self.extract_from_dated_records(key, date)
            records[date] = doses
        return records

    @cached_property
    def boosted(self):
        key = 'booster_recip_count'
        records = {}
        for date in self.dates:
            doses = self.extract_from_dated_records(key, date)
            records[date] = doses
        return records

    @cached_property
    def dates(self):
        dates = []

        # Fencepost alert: Don't forget to add one to range to include final day.
        for n in range(int((self.ends_on - self.starts_on).days) + 1):
            date = self.starts_on + timedelta(n)
            dates.append(date)

        return dates

    @property
    def starts_on(self):
        return self.date_str_to_date(START_DATE)

    @property
    def ends_on(self):
        return self.reported_dates[-1]

    #
    # Instance Methods
    #
    def __init__(self):
        pass

    #
    # Private
    #
    @cached_property
    def dated_records(self):
        records = {}
        for record in self.records:
            date = self.date_str_to_date(record['administered_date'])
            records[date] = record
        return records

    @cached_property
    def reported_dates(self):
        return sorted(self.dated_records.keys())

    @cached_property
    def json_data(self):
        json_data = self.fetch_json_data(self.url)
        return json_data

    def fetch_json_data(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def extract_from_dated_records(self, key, date):
        record = self.dated_records.get(date)
        if not record:
            return 0
        return int(record.get(key))

    def date_str_to_date(self, date_str):
        format = '%Y-%m-%d'
        return datetime.strptime(date_str, format).date()


#
# For testing
# python covid_app/extracts/cdph/oc_vaccines_daily_extract.py
#
if __name__ == "__main__":
    extract = OcVaccinesDailyExtract()
    breakpoint()

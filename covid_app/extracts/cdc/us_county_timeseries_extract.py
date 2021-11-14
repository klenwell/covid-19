"""
United States COVID-19 County Timeseries Extract

https://covid.cdc.gov/covid-data-tracker/#county-view|Risk|community_transmission_level
https://covid.cdc.gov/covid-data-tracker/COVIDData/getAjaxData
https://covid.cdc.gov/covid-data-tracker/COVIDData/getAjaxData?id=integrated_county_timeseries_fips_26081_external

Sample Record (key: ):
fips_code	26081
state	"MI"
state_name	"Michigan"
county	"Kent County"
new_cases_7_day_rolling_average	"173.571"
new_deaths_7_day_rolling_average	"suppressed"
new_test_results_reported_7_day_rolling_average	2097
percent_new_test_results_reported_positive_7_day_rolling_average	9.53
admissions_covid_confirmed_7_day_rolling_average	20.86
percent_adult_inpatient_beds_used_confirmed_covid	13.62
percent_adult_icu_beds_used_confirmed_covid	36.37
date	"2021-05-14"
report_date_window_start	"2021-05-08"
report_date_window_end	"2021-05-14"
community_transmission_level	"high"
"""
import requests
from datetime import datetime, date
from functools import cached_property


EXTRACT_URL = 'https://covid.cdc.gov/covid-data-tracker/COVIDData/getAjaxData'
DATASET_ID_F = 'integrated_county_timeseries_fips_{}_external'
TIMESERIES_DATA_KEY = 'integrated_county_timeseries_external_data'
KENT_FIPS = '26081'
DATE_F = '%Y-%m-%d'
START_DATE = date(2020, 3, 1)


class CdcCountyTimeseriesExtract:
    #
    # Static Methods
    #
    @staticmethod
    def kent_mi_daily_extract():
        """Returns instance of extract.
        """
        extract = CdcCountyTimeseriesExtract(fips=KENT_FIPS)
        extract.fetch_data_source()
        return extract

    #
    # Properties
    #
    @cached_property
    def data_dict(self):
        data_dict = {}
        for daily_data in self.json[TIMESERIES_DATA_KEY]:
            date_str = str(daily_data['date'])
            reported_on = datetime.strptime(date_str, DATE_F).date()
            data_dict[reported_on] = daily_data
        return data_dict

    @cached_property
    def dates(self):
        return sorted(self.data_dict.keys())

    @cached_property
    def last_date(self):
        return self.dates[-1]


    @cached_property
    def new_cases(self):
        col_name = 'new_cases_7_day_rolling_average'
        return self.daily_totals(col_name)

    @cached_property
    def new_deaths(self):
        col_name = 'new_death'
        return self.daily_totals(col_name)

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
    def __init__(self, fips=None):
        self.url = EXTRACT_URL
        self.fips = fips
        self.json = None

    def fetch_data_source(self):
        params = {'id': self.county_id}

        response = requests.get(self.url, params=params)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        self.json = response.json()

        return self.json

    #
    # Private
    #
    @property
    def county_id(self):
        return DATASET_ID_F.format(self.fips)

    @cached_property
    def daily_logs(self):
        daily_logs = {}

        for daily_co_data in self.json[TIMESERIES_DATA_KEY]:
            date_str = daily_co_data['date']
            dated = datetime.strptime(date_str, DATE_F).date()
            daily_logs[dated] = daily_co_data

        return daily_logs

    def daily_column(self, dated, column):
        data_on_date = self.data_dict.get(dated, {})
        return data_on_date.get(column)

from os.path import join as path_join
import csv
from functools import cached_property
from datetime import date

from config.app import DATA_ROOT
from covid_app.extracts.cdc.us_county_timeseries_extract import CdcCountyTimeseriesExtract
from covid_app.extracts.ny_times_covid19 import NyTimesCovid19Extract


#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'mi')
EXPORT_FILE_NAME = 'kent-daily.csv'
START_DATE = date(2020, 3, 10)

CSV_HEADER = [
    'Date',
    'New Tests (7d Avg)',
    'Positive Tests (7d Avg)',
    'Positive Test Rate (7d Avg)',
    'New Cases (NYT)',
    'New Deaths (NYT)',
    'Hospital Beds Used %',
    'ICU Bed Used  %',
    'Community Risk',
    '/\\/\\/\\',
    'Total Cases (NYT)',
    'Total Deaths (NYT)',
    'New Cases (CDC)',
    'New Deaths (CDC)'
]


class KentDailyCovidExport:
    #
    # Properties
    #
    @property
    def csv_path(self):
        return path_join(CSV_DATA_PATH, EXPORT_FILE_NAME)

    @cached_property
    def cdc_timeseries_extract(self):
        return CdcCountyTimeseriesExtract.kent_mi_daily_extract()

    @cached_property
    def ny_times_extract(self):
        return NyTimesCovid19Extract.kent_mi_daily_extract()

    @property
    def dates(self):
        return sorted(self.cdc_timeseries_extract.dates)

    #
    # Instance Method
    #
    def __init__(self):
        pass

    def to_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                if dated < START_DATE:
                    continue
                writer.writerow(self.extract_data_to_csv_row(dated))

        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        return [
            dated,
            self.cdc_timeseries_extract.new_tests.get(dated),
            self.cdc_timeseries_extract.new_positive_tests.get(dated),
            self.cdc_timeseries_extract.new_positive_test_pct.get(dated),
            self.ny_times_extract.daily_logs.get(dated, {}).get('new_cases'),
            self.ny_times_extract.daily_logs.get(dated, {}).get('new_deaths'),
            self.cdc_timeseries_extract.pct_hosp_beds_used.get(dated),
            self.cdc_timeseries_extract.pct_icu_beds_used.get(dated),
            self.cdc_timeseries_extract.community_risk.get(dated),
            ' ',
            self.ny_times_extract.daily_logs.get(dated, {}).get('total_cases'),
            self.ny_times_extract.daily_logs.get(dated, {}).get('total_deaths'),
            self.cdc_timeseries_extract.new_cases.get(dated),
            self.cdc_timeseries_extract.new_deaths.get(dated)
        ]

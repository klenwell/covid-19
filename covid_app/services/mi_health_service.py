"""
Michigan Health Service
"""
from os.path import join as path_join
from datetime import date
import csv
from functools import cached_property

from config.app import DATA_ROOT
from covid_app.extracts.ny_times_covid19 import NyTimesCovid19Extract
from covid_app.extracts.us_gov_covid19 import UsGovCovid19Extract


START_DATE = date(2020, 3, 10)
MI_DATA_PATH = path_join(DATA_ROOT, 'mi')
MI_ARCHIVE_PATH = path_join(MI_DATA_PATH, 'daily')


class MiServiceError(Exception):
    pass


class MiHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_kent_csv():
        service = MiHealthService()
        service.to_csv()

    #
    # Properties
    #
    @property
    def daily_csv_headers(self):
        return [
            'Date',
            'Total Cases',
            'Total Deaths',
            'New Cases',
            'New Deaths',
            'New Tests'
        ]

    @property
    def daily_csv_path(self):
        return path_join(MI_DATA_PATH, 'kent-daily.csv')

    @cached_property
    def us_gov_extract(self):
        return UsGovCovid19Extract()

    @cached_property
    def ny_times_extract(self):
        return NyTimesCovid19Extract()

    @cached_property
    def daily_ny_times_logs_for_kent_county(self):
        daily_logs = {}

        source_stream = self.ny_times_extract.fetch_source_stream()
        daily_rows = self.ny_times_extract.filter_kent_mi_data(source_stream)

        for row in daily_rows:
            date, total_cases, total_deaths, new_cases, new_deaths = row
            daily_data = {
                'new_cases': new_cases,
                'new_deaths': new_deaths,
                'total_cases': total_cases,
                'total_deaths': total_deaths
            }
            daily_logs[date] = daily_data

        return daily_logs

    @property
    def dates(self):
        return sorted(self.daily_ny_times_logs_for_kent_county.keys())

    #
    # Instance Method
    #
    def __init__(self):
        pass

    def to_csv(self):
        with open(self.daily_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.daily_csv_headers)

            for dated in reversed(self.dates):
                writer.writerow(self.data_to_csv_row(dated))

        return self.daily_csv_path

    #
    # Private
    #
    def data_to_csv_row(self, dated):
        ny_times_log = self.daily_ny_times_logs_for_kent_county.get(dated, {})

        return [
            dated,
            ny_times_log.get('total_cases'),
            ny_times_log.get('total_deaths'),
            ny_times_log.get('new_cases'),
            ny_times_log.get('new_deaths'),
            self.us_gov_extract.daily_kent_tests.get(dated)
        ]

    def extract_daily_data_rows(self):
        daily_cases = NyTimesCovid19Extract.kent_mi_daily_data()

        try:
            daily_tests = UsGovCovid19Extract.kent_daily_tests()
        except Exception as e:
            print('Failed to fetch tests: {}'.format(e))
            daily_tests = {}

        rows = self.collate_daily_data(daily_cases, daily_tests)
        return rows

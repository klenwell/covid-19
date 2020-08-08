from os.path import join as path_join
import csv
from functools import cached_property
from datetime import date

from config.app import DATA_ROOT
from covid_app.extracts.atlantic_covid_tracking import AtlanticCovidTrackingExtract
from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract


US_DATA_PATH = path_join(DATA_ROOT, 'us')
US_ARCHIVE_PATH = path_join(US_DATA_PATH, 'daily')
START_DATE = date(2020, 3, 1)


class USServiceError(Exception):
    pass


class USHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        service = USHealthService()
        csv_path = service.to_csv()
        return {
            'CSV Path': csv_path,
            'Rows': len(service.dates),
            'Start Date': service.dates[0],
            'Last Date': service.dates[-1]
        }

    #
    # Properties
    #
    @property
    def daily_csv_headers(self):
        return [
            'Date',
            'New Tests',
            'New Cases',
            'New Deaths',
            'Hospital Cases',
            'ICU Cases',
            'Rt'
        ]

    @property
    def daily_csv_path(self):
        return path_join(US_DATA_PATH, 'us-daily.csv')

    @cached_property
    def atlantic_extract(self):
        return AtlanticCovidTrackingExtract()

    @cached_property
    def rt_rates(self):
        return Covid19ProjectionsExtract.us_effective_reproduction()

    @property
    def dates(self):
        return sorted(self.atlantic_extract.dates)

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
        return [
            dated,
            self.atlantic_extract.new_tests.get(dated),
            self.atlantic_extract.new_cases.get(dated),
            self.atlantic_extract.new_deaths.get(dated),
            self.atlantic_extract.hospitalizations.get(dated),
            self.atlantic_extract.icu_cases.get(dated),
            self.rt_rates.get(dated),
        ]

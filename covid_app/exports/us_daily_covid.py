from os.path import join as path_join
import csv
from functools import cached_property

from config.app import DATA_ROOT
from covid_app.extracts.cdc.us_daily_cases_extract import CdcDailyCasesExtract
from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract


#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'us')
EXPORT_FILE_NAME = 'us-daily.csv'

CSV_HEADER = [
    'Date',
    'New Tests',
    'New Cases',
    'New Deaths',
    'Hospital Cases',
    'ICU Cases',
    'Rt'
]


class USDailyCovidExport:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        export = USDailyCovidExport()
        csv_path = service.to_csv()
        return {
            'CSV Path': csv_path,
            'Rows': len(export.dates),
            'Start Date': export.starts_on,
            'Last Date': export.ends_on
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
    def csv_path(self):
        return path_join(CSV_DATA_PATH, EXPORT_FILE_NAME)

    @cached_property
    def cdc_daily_case_extract(self):
        return CdcDailyCasesExtract()

    @cached_property
    def rt_rates(self):
        return Covid19ProjectionsExtract.us_effective_reproduction()

    @property
    def dates(self):
        return sorted(self.cdc_daily_case_extract.dates)

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
                writer.writerow(self.extract_data_to_csv_row(dated))

        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        return [
            dated,
            #self.cdc_daily_case_extract.new_tests.get(dated),
            'N/A',
            self.cdc_daily_case_extract.new_cases.get(dated),
            self.cdc_daily_case_extract.new_deaths.get(dated),
            #self.cdc_daily_case_extract.hospitalizations.get(dated),
            'N/A',
            #self.cdc_daily_case_extract.icu_cases.get(dated),
            'N/A',
            self.rt_rates.get(dated),
        ]

from os.path import join as path_join
import csv
from functools import cached_property

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.extracts.oc_hca.vaccines_summary_extract import OCVaccinesSummaryExtract
from covid_app.extracts.oc_hca.vaccines_daily_extract import OCVaccinesDailyExtract


#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-immunity.csv'

CSV_HEADER = [
    'Date',
    'Population (Est)',
    'Vulnerable',
    'Infectious',
    'Recovered',
    'Vaccinated'
]

OC_POPULATION = 3000000


class OCImmunityExport:
    #
    # Properties
    #
    @property
    def csv_path(self):
        return path_join(CSV_DATA_PATH, EXPORT_FILE_NAME)

    @cached_property
    def oc_daily_case_extract(self):
        return DailyCovid19Extract.latest()

    @property
    def dates(self):
        return sorted(self.oc_daily_case_extract.dates)

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
            OC_POPULATION,
            self.vulnerable_on_date(dated),
            self.infectious_on_date(dated),
            self.recovered_on_date(dated),
            self.vaccinated_on_date(dated)
        ]

    def vulnerable_on_date(self, dated):
        return 'TBA'

    def infectious_on_date(self, dated):
        return 'TBA'

    def recovered_on_date(self, dated):
        return 'TBA'

    def vaccinated_on_date(self, dated):
        return 'TBA'

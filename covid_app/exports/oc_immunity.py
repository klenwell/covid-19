from os.path import join as path_join
import csv
from functools import cached_property
from datetime import timedelta
import time

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.extracts.oc_hca.vaccines_daily_extract import OCVaccinesDailyExtract


#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-immunity.csv'

CSV_HEADER = [
    'Date',
    'Infectious',
    'Recovered',
    'Vaccinated',
    'Vulnerable'
]

OC_POPULATION = 3000000
INFECTIOUS_WINDOW = 14              # days
VACCINE_IMMUNITY_WINDOW = 9 * 30    # days
INFECTION_IMMUNITY_WINDOW = 6 * 30  # days

# This is the factor by which positive cases are estimated to have been undercounted.
# Probably conservative. There are various studies that put the number between 4 and 7.
UNDERTEST_FACTOR = 2.5

# Need to adjust down vaccination count since one dose does not equal full vaccination
# for a vaccine that requires more than one shot. Also none are 100% effective.
VAX_EFFICACY_FACTOR = 0.45


class OCImmunityExport:
    #
    # Properties
    #
    @property
    def csv_path(self):
        return path_join(CSV_DATA_PATH, EXPORT_FILE_NAME)

    @cached_property
    def case_extract(self):
        return DailyCovid19Extract.latest()

    @cached_property
    def vax_extract(self):
        return OCVaccinesDailyExtract()

    @property
    def dates(self):
        return sorted(self.case_extract.dates)

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    @property
    def run_time(self):
        if not self.run_time_end:
            return None

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self):
        self.run_time_start = time.time()

    def to_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                writer.writerow(self.extract_data_to_csv_row(dated))

        self.run_time_end = time.time()
        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        infectious = round(self.infectious_on_date(dated))
        recovered = round(self.recovered_on_date(dated))
        vaccinated = round(self.vaccinated_on_date(dated))
        vulnerable = OC_POPULATION - infectious - recovered - vaccinated

        return [
            dated,
            infectious,
            recovered,
            vaccinated,
            vulnerable
        ]

    def infectious_on_date(self, dated):
        infections = []
        extract = self.case_extract
        start_date = dated - timedelta(days=INFECTIOUS_WINDOW)

        for n in range(INFECTIOUS_WINDOW):
            on_date = start_date + timedelta(days=n)
            infection_count = extract.new_positive_tests_administered.get(on_date, 0) or 0
            infection_count = infection_count * UNDERTEST_FACTOR
            infections.append(infection_count)

        return sum(infections)

    def recovered_on_date(self, dated):
        recovered = []
        extract = self.case_extract
        start_date = dated - timedelta(days=INFECTION_IMMUNITY_WINDOW)
        end_date = dated - timedelta(days=INFECTIOUS_WINDOW)
        days = (end_date - start_date).days

        for n in range(days):
            on_date = start_date + timedelta(days=n)
            recovered_count = extract.new_positive_tests_administered.get(on_date, 0)
            recovered_count = recovered_count * UNDERTEST_FACTOR
            recovered.append(recovered_count)

        return sum(recovered)

    def vaccinated_on_date(self, dated):
        vaccinated = []
        start_date = dated - timedelta(days=VACCINE_IMMUNITY_WINDOW)
        end_date = dated
        days = (end_date - start_date).days

        for n in range(days):
            on_date = start_date + timedelta(days=n)
            dose_count = self.vax_extract.daily_doses.get(on_date, 0)
            vax_count = float(dose_count) * VAX_EFFICACY_FACTOR
            vaccinated.append(vax_count)

        return sum(vaccinated)

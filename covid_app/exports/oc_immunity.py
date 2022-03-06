from os.path import join as path_join
import csv
from functools import cached_property
from datetime import timedelta
import time

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.extracts.cdph.oc_vaccines_daily_extract import OcVaccinesDailyExtract
from covid_app.models.oc.immune_cohort import ImmuneCohort

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
    'Vulnerable',
    'Partial Vax',
    'Fully Vax',
    'Booster'
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
        return OcVaccinesDailyExtract()

    @cached_property
    def estimates(self):
        estimates = []
        cohorts = []

        # Note here: update_boosted_cohorts requires cycling through cohorts from oldest
        # to newest.
        for dated in self.dates:
            partial_vax = self.vax_extract.partially_vaccinated.get(dated, 0) or 0
            full_vax = self.vax_extract.fully_vaccinated.get(dated, 0) or 0
            boosted = self.vax_extract.boosted.get(dated, 0) or 0
            infected = self.case_extract.new_positive_tests_administered.get(dated, 0) or 0

            cohort = ImmuneCohort(dated, partial_vax, full_vax, boosted, infected)
            cohort.update_boosted_cohorts(cohorts)
            cohorts.append(cohort)

            if len(cohorts) > 401:
                spy = cohorts[400]
                print(dated, spy.date, spy.unboosted_full_vaxxed, spy.compute_vax_immunity_for_date(dated))

            estimate = {
                'date': dated,
                'infectious': ImmuneCohort.count_active_infections(cohorts),
                'recovered': sum([c.compute_recovered_immunity_for_date(dated) for c in cohorts]),
                'vaccinated': sum([c.compute_vax_immunity_for_date(dated) for c in cohorts]),
                'partial_vax': partial_vax,
                'full_vax': full_vax,
                'boosted': boosted
            }
            estimates.append(estimate)

        return estimates

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

            for estimate in reversed(self.estimates):
                writer.writerow(self.extract_data_to_csv_row(estimate))

        self.run_time_end = time.time()
        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, estimate):
        infectious = round(estimate['infectious'])
        recovered = round(estimate['recovered'])
        vaccinated = round(estimate['vaccinated'])
        vulnerable = OC_POPULATION - infectious - recovered - vaccinated

        return [
            estimate['date'],
            infectious,
            recovered,
            vaccinated,
            vulnerable,
            estimate['partial_vax'],
            estimate['full_vax'],
            estimate['boosted']
        ]

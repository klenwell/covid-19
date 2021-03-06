"""
Orange County Health Service

Uses OC HCA API. For more information, see:

https://occovid19.ochealthinfo.com/coronavirus-in-oc
"""
from os.path import join as path_join
from datetime import date, datetime, timedelta
import csv
from functools import cached_property

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.extracts.covid_act_now import CovidActNowExtract
from covid_app.extracts.unacast_social_distancing import UnacastSocialDistancingExtract


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ARCHIVE_PATH = path_join(OC_DATA_PATH, 'daily')


class OCServiceError(Exception):
    pass


class OCHealthService:
    VERSION = '1.1'

    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        service = OCHealthService()
        service.to_csv()
        return service

    @staticmethod
    def export_archive(archive_url):
        extract = DailyCovid19Extract.archive(archive_url)
        service = OCHealthService()
        rows = service.extract_archive_rows(extract)
        result = service.output_archive_csv(rows, archive_url, extract.VERSION)
        return result

    #
    # Properties
    #
    @property
    def daily_csv_headers(self):
        return [
            'Date',
            'New Tests Administered',
            'Pos Tests Administered',
            'New Tests Reported',
            'New Cases',
            'Hospitalizations',
            'ICU',
            'New Deaths',
            'Rt Rate',
            'Travel Distance',
            'Visitation',
            'Encounter Density',
            'Social Distance Grade',
            'SNF Cases'
        ]

    @property
    def daily_csv_path(self):
        return path_join(OC_DATA_PATH, 'oc-hca.csv')

    @cached_property
    def oc_hca_extract(self):
        return DailyCovid19Extract.latest()

    @cached_property
    def unacast_extract(self):
        return UnacastSocialDistancingExtract.oc()

    @cached_property
    def rt_extract(self):
        return CovidActNowExtract.oc_effective_reproduction()

    @cached_property
    def daily_csv_rows(self):
        rows = []
        next_date = self.daily_csv_start_date

        while next_date <= self.daily_csv_end_date:
            row = self.daily_csv_row_for_date(next_date)
            rows.append(row)
            next_date = next_date + timedelta(days=1)

        return sorted(rows, key=lambda r: r[0], reverse=True)

    @cached_property
    def daily_csv_start_date(self):
        return self.oc_hca_extract.starts_on

    @cached_property
    def daily_csv_end_date(self):
        return self.oc_hca_extract.ends_on

    @property
    def start_date(self):
        return self.oc_hca_extract.starts_on

    @property
    def end_date(self):
        return self.oc_hca_extract.ends_on

    @property
    def dates(self):
        return self.oc_hca_extract.dates

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

    def data_to_csv_row(self, dated):
        return [
            dated,
            self.oc_hca_extract.new_tests_administered.get(dated),
            self.oc_hca_extract.new_positive_tests_administered.get(dated),
            self.oc_hca_extract.new_tests_reported.get(dated),
            self.oc_hca_extract.new_cases.get(dated),
            self.oc_hca_extract.hospitalizations.get(dated),
            self.oc_hca_extract.icu_cases.get(dated),
            self.oc_hca_extract.new_deaths.get(dated),
            self.rt_extract.infection_rates.get(dated),
            self.unacast_extract.travel_distance_scores.get(dated),
            self.unacast_extract.visitation_scores.get(dated),
            self.unacast_extract.encounter_densities.get(dated),
            self.unacast_extract.grades.get(dated),
            self.oc_hca_extract.new_snf_cases.get(dated)
        ]

    #
    # Archive Methods
    #
    def extract_archive_rows(self, extract):
        rows = []

        # Start on 3/1/2020.
        next_date = date(2020, 3, 1)

        while next_date <= extract.ends_on:
            daily_cases = extract.new_cases.get(next_date, '')
            daily_tests = extract.new_tests.get(next_date, '')
            daily_hosps = extract.hospitalizations.get(next_date, '')
            daily_icus = extract.icu_cases.get(next_date, '')

            row = [next_date, daily_cases, daily_tests, daily_hosps, daily_icus]
            rows.append(row)

            next_date = next_date + timedelta(days=1)

        return rows

    def output_archive_csv(self, rows, archive_url, extract_version):
        archive_headers = ['Date', 'New Cases', 'New Tests', 'Hosp', 'ICU']

        rows = sorted(rows, key=lambda r: r[0], reverse=True)
        start_date = rows[-1][0]
        end_date = rows[0][0]

        csv_fname = 'oc-hca-{}.csv'.format(end_date.strftime('%Y%m%d'))
        csv_path = path_join(OC_ARCHIVE_PATH, csv_fname)
        footer = 'exported from {} at {}'.format(archive_url, datetime.now().isoformat())

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(archive_headers)

            for row in rows:
                writer.writerow(row)

            writer.writerow([])
            writer.writerow([footer])

        return {
            'path': csv_path,
            'rows': len(rows),
            'start_date': start_date,
            'end_date': end_date,
            'extract_version': extract_version
        }

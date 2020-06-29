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
from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ARCHIVE_PATH = path_join(OC_DATA_PATH, 'daily')


class OCServiceError(Exception):
    pass


class OCHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        service = OCHealthService()
        result = service.output_daily_csv()
        return result

    @staticmethod
    def export_archive(archive_url):
        service = OCHealthService(archive_url=archive_url)
        rows = service.extract_archive_data_rows()
        result = service.output_archive_csv(rows)
        return result

    #
    # Properties
    #
    @property
    def daily_csv_headers(self):
        return [
            'Date',
            'New Cases',
            'New Tests',
            'Hospitalizations',
            'ICU',
            'New Deaths',
            'Rt Rate'
        ]

    @property
    def daily_csv_path(self):
        return path_join(OC_DATA_PATH, 'oc-hca.csv')

    @cached_property
    def daily_extract(self):
        return DailyCovid19Extract.latest()

    @cached_property
    def extract_version(self):
        return self.daily_extract.VERSION

    @cached_property
    def daily_rts(self):
        return Covid19ProjectionsExtract.oc_effective_reproduction()

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
        return self.daily_extract.starts_on

    @cached_property
    def daily_csv_end_date(self):
        return self.daily_extract.ends_on

    #
    # Instance Method
    #
    def __init__(self, archive_url=None):
        self.archive_url = archive_url

    def output_daily_csv(self):
        with open(self.daily_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.daily_csv_headers)

            for row in self.daily_csv_rows:
                writer.writerow(row)

        return {
            'path': self.daily_csv_path,
            'rows': len(self.daily_csv_rows),
            'start_date': self.daily_csv_start_date,
            'end_date': self.daily_csv_end_date,
            'extract_version': self.extract_version
        }

    def daily_csv_row_for_date(self, dated):
        return [
            dated,
            self.daily_extract.new_cases.get(dated),
            self.daily_extract.new_tests.get(dated),
            self.daily_extract.hospitalizations.get(dated),
            self.daily_extract.icu_cases.get(dated),
            self.daily_extract.new_deaths.get(dated),
            self.daily_rts.get(dated)
        ]

    def extract_archive_data_rows(self):
        extract = DailyCovid19Extract.archive(self.archive_url)
        self.extract_version = extract.VERSION
        deaths = {}     # Skip deaths in archive.
        rt_rates = {}   # Skip in archive.
        rows = self.collate_archive_data(extract, deaths, rt_rates)
        return rows

    def collate_archive_data(self, extract, deaths, rts):
        rows = []

        # Start on 3/1/2020.
        next_date = date(2020, 3, 1)

        while next_date <= extract.ends_on:
            daily_cases = extract.new_cases.get(next_date, '')
            daily_tests = extract.new_tests.get(next_date, '')
            daily_hosps = extract.hospitalizations.get(next_date, '')
            daily_icus = extract.icu_cases.get(next_date, '')
            daily_deaths = deaths.get(next_date, '')
            daily_rts = rts.get(next_date, '')

            row = [next_date, daily_cases, daily_tests, daily_hosps, daily_icus, daily_deaths,
                   daily_rts]
            rows.append(row)

            next_date = next_date + timedelta(days=1)

        return rows

    def output_archive_csv(self, rows):
        archive_date = rows[-1][0]
        csv_fname = 'oc-hca-{}.csv'.format(archive_date.strftime('%Y%m%d'))
        csv_path = path_join(OC_ARCHIVE_PATH, csv_fname)
        footer = 'exported from {} at {}'.format(self.archive_url, datetime.now().isoformat())

        return self.output_daily_csv(rows, csv_path=csv_path, footer=footer)

"""
Orange County Health Service

Uses OC HCA API. For more information, see:

https://occovid19.ochealthinfo.com/coronavirus-in-oc
"""
from os.path import join as path_join
from datetime import date, datetime, timedelta
import csv

from config.app import DATA_ROOT
from covid_app.extracts.oc_hca.daily_covid19_extract import DailyCovid19Extract
from covid_app.extracts.ny_times_covid19 import NyTimesCovid19Extract
from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract


SERVICE_URL = 'https://occovid19.ochealthinfo.com/coronavirus-in-oc'
SERVICE_DATE_F = '%m/%d/%Y'
START_DATE = date(2020, 3, 1)
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
        rows = service.extract_daily_data_rows()
        result = service.output_daily_csv(rows)
        return result

    @staticmethod
    def export_archive(archive_url):
        service = OCHealthService(archive_url=archive_url)
        rows = service.extract_archive_data_rows()
        result = service.output_archive_csv(rows)
        return result

    #
    # Instance Method
    #
    def __init__(self, archive_url=None):
        self.archive_url = archive_url
        self.extract_version = 'n/a'

    def extract_daily_data_rows(self, source_url=None):
        extract = DailyCovid19Extract.latest()
        self.extract_version = extract.VERSION
        deaths = NyTimesCovid19Extract.oc_daily_deaths()
        rt_rates = Covid19ProjectionsExtract.oc_effective_reproduction()
        rows = self.collate_daily_data(extract, deaths, rt_rates)
        return rows

    def extract_archive_data_rows(self):
        extract = DailyCovid19Extract.archive(self.archive_url)
        self.extract_version = extract.VERSION
        deaths = {}     # Skip deaths in archive.
        rt_rates = {}   # Skip in archive.
        rows = self.collate_daily_data(extract, deaths, rt_rates)
        return rows

    def collate_daily_data(self, extract, deaths, rts):
        rows = []

        start_on = START_DATE
        next_date = start_on

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

    def output_daily_csv(self, rows, csv_path=None, footer=None):
        if not csv_path:
            csv_path = path_join(OC_DATA_PATH, 'oc-hca.csv')

        header_row = ['Date', 'New Cases', 'New Tests', 'Hospitalizations', 'ICU', 'New Deaths',
                      'Rt Rate']
        rows_by_most_recent = sorted(rows, key=lambda r: r[0], reverse=True)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header_row)
            for row in rows_by_most_recent:
                writer.writerow(row)

            if footer:
                writer.writerow([])
                writer.writerow([footer])

        return {
            'path': csv_path,
            'rows': len(rows_by_most_recent),
            'start_date': rows_by_most_recent[-1][0],
            'end_date': rows_by_most_recent[0][0],
            'extract_version': self.extract_version
        }

    def output_archive_csv(self, rows):
        archive_date = rows[-1][0]
        csv_fname = 'oc-hca-{}.csv'.format(archive_date.strftime('%Y%m%d'))
        csv_path = path_join(OC_ARCHIVE_PATH, csv_fname)
        footer = 'exported from {} at {}'.format(self.archive_url, datetime.now().isoformat())

        return self.output_daily_csv(rows, csv_path=csv_path, footer=footer)

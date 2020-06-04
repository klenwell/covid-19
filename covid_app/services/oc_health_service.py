"""
Orange County Health Service

Uses OC HCA API. For more information, see:

https://occovid19.ochealthinfo.com/coronavirus-in-oc
"""
from os.path import join as path_join
from datetime import datetime, timedelta
import json
import csv
import requests

from config.app import DATA_ROOT


SERVICE_URL = 'https://occovid19.ochealthinfo.com/coronavirus-in-oc'
SERVICE_DATE_F = '%m/%d/%Y'
START_DATE = '3/1/2020'
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
        service = OCHealthService(archive=archive_url)
        rows = service.extract_daily_data_rows()
        result = service.output_archive_csv(rows)
        return result

    #
    # Instance Method
    #
    def __init__(self, archive=None):
        self.url = SERVICE_URL

        if archive:
            self.url = archive

        # To adjust for changes in OC HCA data formatting as embedded in page source.
        self.format_version = None

    def extract_daily_data_rows(self, source_url=None):
        html = self.fetch_page_source(source_url)
        self.format_version = self.detect_format_version(html)

        new_tests = self.extract_new_tests(html)
        new_cases = self.extract_new_cases(html)
        hosps, icus = self.extract_hospitalizations(html)
        rows = self.collate_daily_data(new_cases, new_tests, hosps, icus)
        return rows

    def output_daily_csv(self, rows, csv_path=None, footer=None):
        if not csv_path:
            csv_path = path_join(OC_DATA_PATH, 'oc-hca.csv')

        header_row = ['Date', 'New Cases', 'New Tests', 'Hospitalizations', 'ICU']
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
            'format_version': self.format_version
        }

    def output_archive_csv(self, rows):
        archive_date = rows[-1][0]
        csv_fname = 'oc-hca-{}.csv'.format(archive_date.strftime('%Y%m%d'))
        csv_path = path_join(OC_ARCHIVE_PATH, csv_fname)
        footer = 'exported from {} at {}'.format(self.url, datetime.now().isoformat())

        return self.output_daily_csv(rows, csv_path=csv_path, footer=footer)

    def fetch_page_source(self, source_url=None):
        if not source_url:
            source_url = self.url
        response = requests.get(source_url)

        # This will raise a requests.exceptions.HTTPError error for caller to handle.
        response.raise_for_status()

        return response.text

    def detect_format_version(self, html):
        v1_needle = 'caseArr ='
        v2_needle = '$cases ='  # update on 2020-06-03

        if v1_needle in html:
            return 1
        elif v2_needle in html:
            return 2
        else:
            raise OCServiceError('Page source formatting not recognized.')

    def extract_new_cases(self, html):
        new_cases = {}

        # Default extract parameters
        needle = '$cases ='
        count_idx = 1

        # Adjust extract parameters based on version
        if self.format_version == 1:
            needle = 'caseArr ='

        _, tail = html.split(needle)
        payload, _ = tail.split(';', 1)
        daily_cases = json.loads(payload)

        for case in daily_cases:
            case_date = datetime.strptime(case[0], SERVICE_DATE_F).date()
            case_count = case[count_idx]
            new_cases[case_date] = case_count

        return new_cases

    def extract_new_tests(self, html):
        new_tests = {}

        # Default extract parameters
        needle = '$pplData ='
        count_idx = 2

        # Adjust extract parameters based on version
        if self.format_version == 1:
            needle = 'testData ='

        try:
            _, tail = html.split(needle)
            payload, _ = tail.split(';', 1)
            daily_tests = json.loads(payload)
        except ValueError as e:
            print("Failed to extract new tests: {}".format(e))
            return {}

        for test in daily_tests:
            test_date = datetime.strptime(test[0], SERVICE_DATE_F).date()
            test_count = test[count_idx]
            new_tests[test_date] = test_count

        return new_tests

    def extract_hospitalizations(self, html):
        new_hospitalizations = {}
        new_icu_cases = {}

        # Default extract parameters
        needle = '$hospitalData ='
        hosp_idx = 1
        icu_idx = 2

        # Adjust extract parameters based on version
        if self.format_version == 1:
            needle = 'hospitalArr ='

        try:
            _, tail = html.split(needle)
            payload, _ = tail.split(';', 1)
            daily_hospitalizations = json.loads(payload)
        except ValueError as e:
            print("Failed to extract hospitalizations: {}".format(e))
            return {}, {}

        for daily in daily_hospitalizations:
            case_date = datetime.strptime(daily[0], SERVICE_DATE_F).date()
            hosp_count = daily[hosp_idx]
            icu_count = daily[icu_idx]
            new_hospitalizations[case_date] = hosp_count
            new_icu_cases[case_date] = icu_count

        return new_hospitalizations, new_icu_cases

    def collate_daily_data(self, cases, tests, hosps, icus):
        rows = []

        start_on = datetime.strptime(START_DATE, SERVICE_DATE_F).date()
        end_on = self.extract_latest_date_from_new_cases(cases)
        next_date = start_on

        while next_date <= end_on:
            daily_cases = cases.get(next_date, '')
            daily_tests = tests.get(next_date, '')
            daily_hosps = hosps.get(next_date, '')
            daily_icus = icus.get(next_date, '')

            row = [next_date, daily_cases, daily_tests, daily_hosps, daily_icus]
            rows.append(row)

            next_date = next_date + timedelta(days=1)

        return rows

    def extract_latest_date_from_new_cases(self, cases):
        dates = cases.keys()
        sorted_dates = sorted(dates)
        return sorted_dates[-1]

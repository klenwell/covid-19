"""
Orange County Health Service

Uses OC HCA API. For more information, see:

https://occovid19.ochealthinfo.com/coronavirus-in-oc
"""
from functools import cached_property
from datetime import datetime, timedelta
import json
import csv
import requests


SERVICE_URL = 'https://occovid19.ochealthinfo.com/coronavirus-in-oc'
SERVICE_DATE_F = '%m/%d/%Y'
START_DATE = '3/1/2020'


class OCHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        rows = OCHealthService.fetch_daily_data()
        result = OCHealthService.output_daily_csv(rows)
        return result

    @staticmethod
    def fetch_daily_data():
        service = OCHealthService()
        html = service.fetch_page_source()
        new_tests = service.extract_new_tests(html)
        new_cases = service.extract_new_cases(html)
        hosps, icus = service.extract_hospitalizations(html)
        rows = service.collate_daily_data(new_cases, new_tests, hosps, icus)
        return rows

    @staticmethod
    def output_daily_csv(rows):
        csv_path = 'oc_daily.csv'
        header_row = ['Date', 'New Cases', 'New Tests', 'Hospitalizations', 'ICU']
        rows_by_most_recent = sorted(rows, key=lambda r: r[0], reverse=True)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header_row)
            for row in rows_by_most_recent:
                writer.writerow(row)

        return {
            'path': csv_path,
            'rows': len(rows_by_most_recent),
            'start_date': rows_by_most_recent[-1][0],
            'end_date': rows_by_most_recent[0][0]
        }

    #
    # Instance Method
    #
    def __init__(self):
        self.url = SERVICE_URL

    def fetch_page_source(self):
        response = requests.get(self.url)

        # This will raise a requests.exceptions.HTTPError error for caller to handle.
        response.raise_for_status()

        return response.text

    def extract_new_tests(self, html):
        needle = 'testData ='
        new_tests = {}

        _, tail = html.split(needle)
        payload, _ = tail.split(';', 1)
        daily_tests = json.loads(payload)

        for test in daily_tests:
            test_date = datetime.strptime(test[0], SERVICE_DATE_F).date()
            test_count = test[2]
            new_tests[test_date] = test_count

        return new_tests

    def extract_new_cases(self, html):
        needle = 'caseArr ='
        new_cases = {}

        _, tail = html.split(needle)
        payload, _ = tail.split(';', 1)
        daily_cases = json.loads(payload)

        for case in daily_cases:
            case_date = datetime.strptime(case[0], SERVICE_DATE_F).date()
            case_count = case[1]
            new_cases[case_date] = case_count

        return new_cases

    def extract_hospitalizations(self, html):
        needle = 'hospitalArr ='
        new_hospitalizations = {}
        new_icu_cases = {}

        _, tail = html.split(needle)
        payload, _ = tail.split(';', 1)
        daily_hospitalizations = json.loads(payload)

        for daily in daily_hospitalizations:
            case_date = datetime.strptime(daily[0], SERVICE_DATE_F).date()
            hosp_count = daily[1]
            icu_count = daily[2]
            new_hospitalizations[case_date] = hosp_count
            new_icu_cases[case_date] = icu_count

        return new_hospitalizations, new_icu_cases

    def collate_daily_data(self, tests, cases, hosps, icus):
        rows = []

        start_on = datetime.strptime(START_DATE, SERVICE_DATE_F).date()
        end_on = datetime.now().date()
        next_date = start_on

        while next_date <= end_on:
            daily_tests = tests.get(next_date, 0)
            daily_cases = cases.get(next_date, 0)
            daily_hosps = hosps.get(next_date, 0)
            daily_icus = icus.get(next_date, 0)

            row = [next_date, daily_tests, daily_cases, daily_hosps, daily_icus]
            rows.append(row)

            next_date = next_date + timedelta(days=1)

        return rows

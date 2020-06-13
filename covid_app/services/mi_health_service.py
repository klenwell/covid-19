"""
Michigan Health Service
"""
from os.path import join as path_join
from datetime import date
import csv

from config.app import DATA_ROOT
from covid_app.extracts.ny_times_covid19 import NyTimesCovid19Extract
from covid_app.extracts.us_gov_covid19 import UsGovCovid19Extract


START_DATE = date(2020, 3, 10)
MI_DATA_PATH = path_join(DATA_ROOT, 'mi')
MI_ARCHIVE_PATH = path_join(MI_DATA_PATH, 'daily')


class MiServiceError(Exception):
    pass


class MiHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_kent_csv():
        csv_path = path_join(MI_DATA_PATH, 'kent-daily.csv')
        service = MiHealthService()
        rows = service.extract_daily_data_rows()
        result = service.output_daily_csv(rows, csv_path=csv_path)
        return result

    #
    # Instance Method
    #
    def __init__(self):
        pass

    def extract_daily_data_rows(self):
        daily_cases = NyTimesCovid19Extract.kent_mi_daily_data()

        try:
            daily_tests = UsGovCovid19Extract.kent_daily_tests()
        except Exception as e:
            print('Failed to fetch tests: {}'.format(e))
            daily_tests = {}

        rows = self.collate_daily_data(daily_cases, daily_tests)
        return rows

    def output_daily_csv(self, rows, csv_path=None, footer=None):
        header_row = ['Date', 'Total Cases', 'Total Deaths', 'New Cases', 'New Deaths',
                      'New Tests']
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
            'end_date': rows_by_most_recent[0][0]
        }

    #
    # Private
    #
    def collate_daily_data(self, daily_cases, daily_tests):
        """daily_cases are ordered row. daily_tests is a dict with dates as keys.
        """
        rows = []

        # See NyTimesCovid19.filter_kent_mi_data for row data
        for next_date, total_cases, total_deaths, new_cases, new_deaths in daily_cases:
            if next_date < START_DATE:
                continue

            new_tests = daily_tests.get(next_date, '')

            row = [next_date, total_cases, total_deaths, new_cases, new_deaths, new_tests]
            rows.append(row)

        return rows

"""
Michigan Health Service
"""
from os.path import join as path_join
import csv

from config.app import DATA_ROOT
from covid_app.extracts.ny_times_covid19 import NyTimesCovid19Extract


SERVICE_DATE_F = '%m/%d/%Y'
START_DATE = '3/10/2020'
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
        service = MiHealthService()
        rows = NyTimesCovid19Extract.kent_mi_daily_data()
        csv_path = path_join(MI_DATA_PATH, 'kent-daily.csv')
        result = service.output_daily_csv(rows, csv_path=csv_path)
        return result

    #
    # Instance Method
    #
    def __init__(self):
        pass

    def output_daily_csv(self, rows, csv_path=None, footer=None):
        header_row = ['Date', 'Total Cases', 'Total Deaths', 'New Cases', 'New Deaths']
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

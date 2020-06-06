"""
Michigan Health Service
"""
from os.path import join as path_join
from datetime import datetime, timedelta
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

    @staticmethod
    def export_daily_region_6_csv():
        service = MiHealthService()
        data = NyTimesCovid19Extract.mi6_daily_data()
        csv_path = path_join(MI_DATA_PATH, 'mi6-daily.csv')
        result = service.output_daily_regional_csv(data, csv_path=csv_path)
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

    def output_daily_regional_csv(self, data, csv_path=None, footer=None):
        header_row = ['Date', 'New Cases', 'New Deaths']

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header_row)

            start_on = datetime.strptime(START_DATE, SERVICE_DATE_F).date()
            end_on = sorted(data.keys())[-1]
            next_date = end_on

            while next_date >= start_on:
                # datetime.date(2020, 6, 4): {'26035': ('Clare', 19, 2, 0, 0),  ... }
                this_date = next_date
                next_date = this_date - timedelta(days=1)
                daily_data = data.get(this_date)

                if not daily_data:
                    continue

                total_cases = sum([v[3] for v in daily_data.values()])
                total_deaths = sum([v[4] for v in daily_data.values()])
                row = [this_date, total_cases, total_deaths]
                writer.writerow(row)

            if footer:
                writer.writerow([])
                writer.writerow([footer])

        return {
            'path': csv_path,
            'rows': len(data),
            'start_date': start_on,
            'end_date': end_on
        }

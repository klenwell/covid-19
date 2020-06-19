from os.path import join as path_join
import csv
from functools import cached_property
from datetime import date, timedelta

from config.app import DATA_ROOT
from covid_app.extracts.atlantic_covid_tracking import AtlanticCovidTrackingExtract
from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract


US_DATA_PATH = path_join(DATA_ROOT, 'us')
US_ARCHIVE_PATH = path_join(US_DATA_PATH, 'daily')
START_DATE = date(2020, 3, 1)


class USServiceError(Exception):
    pass


class USHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        service = USHealthService()
        rows = service.extract_daily_data_rows()
        result = service.output_daily_csv(rows)
        return result

    #
    # Properties
    #
    @cached_property
    def ordered_extract_rows(self):
        """Ordered by most recent date first
        """
        rows = []
        ordered_dates = sorted(self.extract.dates, reverse=True)

        for dated in ordered_dates:
            row = self.extract.to_csv_row_by_date(dated)
            rows.append(row)

        return rows

    #
    # Instance Method
    #
    def __init__(self):
        self.extract = None

    def extract_daily_data_rows(self):
        self.extract = AtlanticCovidTrackingExtract.us_daily_extract()
        rt_rates = Covid19ProjectionsExtract.us_effective_reproduction()
        rows = self.collate_daily_data(self.extract, rt_rates)
        return rows

    def output_daily_csv(self, rows, footer=None):
        header_row = ['Date', 'New Cases', 'New Tests', 'Hospitalizations', 'ICU', 'New Deaths',
                      'Rt Rate']
        rows_by_most_recent = sorted(rows, key=lambda r: r[0], reverse=True)
        end_date = rows_by_most_recent[0][0]

        csv_file = 'daily-{}.csv'.format(end_date.strftime('%Y%m%d'))
        csv_path = path_join(US_DATA_PATH, csv_file)

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
            'rows': len(rows),
            'start_date': rows[-1][0],
            'end_date': end_date
        }

    #
    # Private
    #
    def collate_daily_data(self, extract, rts):
        rows = []

        start_on = START_DATE
        next_date = start_on

        while next_date <= extract.last_date:
            daily_cases = extract.new_cases.get(next_date, '')
            daily_tests = extract.new_tests.get(next_date, '')
            daily_hosps = extract.hospitalizations.get(next_date, '')
            daily_icus = extract.icu_cases.get(next_date, '')
            daily_deaths = extract.new_deaths.get(next_date, '')
            daily_rts = rts.get(next_date, '')

            row = [next_date, daily_cases, daily_tests, daily_hosps, daily_icus, daily_deaths,
                   daily_rts]
            rows.append(row)

            next_date = next_date + timedelta(days=1)

        return rows

"""
Michigan Health Service
"""
from os.path import join as path_join
import csv
from functools import cached_property

from config.app import DATA_ROOT
from covid_app.extracts.atlantic_covid_tracking import AtlanticCovidTrackingExtract


US_DATA_PATH = path_join(DATA_ROOT, 'us')
US_ARCHIVE_PATH = path_join(US_DATA_PATH, 'daily')


class USServiceError(Exception):
    pass


class USHealthService:
    #
    # Static Methods
    #
    @staticmethod
    def export_daily_csv():
        service = USHealthService()
        service.extract_data()
        result = service.output_daily_csv()
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

    def extract_data(self):
        self.extract = AtlanticCovidTrackingExtract.us_daily_extract()
        return self.extract

    def output_daily_csv(self, footer=None):
        csv_file = 'daily-{}.csv'.format(self.extract.last_date.strftime('%Y%m%d'))
        csv_path = path_join(US_DATA_PATH, csv_file)

        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.extract.header_row)

            for row in self.ordered_extract_rows:
                writer.writerow(row)

            if footer:
                writer.writerow([])
                writer.writerow([footer])

        return {
            'path': csv_path,
            'rows': len(self.ordered_extract_rows),
            'start_date': self.ordered_extract_rows[-1][0],
            'end_date': self.ordered_extract_rows[0][0]
        }

    #
    # Private
    #

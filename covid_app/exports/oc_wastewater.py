from os.path import join as path_join
import csv
from functools import cached_property
import time

from config.app import DATA_ROOT
from covid_app.extracts.cdph.oc_detailed_wastewater_extract import OcWastewaterExtract

#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-wastewater.csv'

CSV_HEADER = [
    'Date',
    'Virus/ml',
    'Site ID',
    'PCR Target',
    'PCR Gene Target',
    'Zip Code',
    'WWTP Name',
    'EPA ID',
    'Lab ID',
    'Sample ID',
    'Virus',
    'Units'
]


class OCWastewaterExport:
    #
    # Properties
    #
    @property
    def csv_path(self):
        return path_join(CSV_DATA_PATH, EXPORT_FILE_NAME)

    @cached_property
    def extract(self):
        return OcWastewaterExtract(self.use_mock)

    @property
    def dates(self):
        return sorted(self.extract.dates)

    @property
    def starts_on(self):
        return self.dates[0]

    @property
    def ends_on(self):
        return self.dates[-1]

    @property
    def newest_oc_sample(self):
        newest = sorted(self.extract.oc_rows, key=lambda r: r['date'], reverse=True)[0]
        return [newest['date'], newest['zipcode'], newest['epaid']]

    @property
    def run_time(self):
        if not self.run_time_end:
            return None

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self, mock=False):
        self.use_mock = mock
        self.run_time_start = time.time()

    def to_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                for row in self.extract_oc_data_to_csv_rows(dated):
                    writer.writerow(row)

        self.run_time_end = time.time()
        return self.csv_path

    #
    # Private
    #
    def extract_oc_data_to_csv_rows(self, dated):
        csv_rows = []
        extract_rows = [r for r in self.extract.oc_rows if r['date'] == dated]

        for extract_row in extract_rows:
            csv_row = [
                dated,
                extract_row.get('virus_ml'),
                extract_row.get('site_id'),
                extract_row.get('pcr_target'),
                extract_row.get('pcr_gene_target'),
                extract_row.get('zipcode'),
                extract_row.get('wwtp_name'),
                extract_row.get('epaid'),
                extract_row.get('lab_id'),
                extract_row.get('sample_id'),
                extract_row.get('virus'),
                extract_row.get('pcr_target_units')
            ]
            csv_rows.append(csv_row)

        return csv_rows

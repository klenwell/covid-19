from os.path import join as path_join
import csv
from functools import cached_property
import time

from config.app import DATA_ROOT
from covid_app.extracts.cdph.oc_wastewater_extract import OcWastewaterExtract

#
# Constants
#
CSV_DATA_PATH = path_join(DATA_ROOT, 'oc')
EXPORT_FILE_NAME = 'oc-wastewater.csv'

CSV_HEADER = [
    'Date',
    'K-Virus 7d Avg',
    'Virus',
    'Virus (k)',
    'Virus (ln)',
    'Rolling 10d Avg',
    'Source',
    'Lab ID',
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
        return OcWastewaterExtract()

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
    def run_time(self):
        if not self.run_time_end:
            return None

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self):
        self.run_time_start = time.time()

    def to_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

            for dated in reversed(self.dates):
                writer.writerow(self.extract_data_to_csv_row(dated))

        self.run_time_end = time.time()
        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        row = self.extract.dated_samples.get(dated, {})

        return [
            dated,
            self.extract.viral_counts_7d_avg.get(dated),
            row.get('virus'),
            row.get('virus_k'),
            row.get('log_virus'),
            row.get('Ten_Rollapply'),
            row.get('data_source'),
            row.get('Lab Id'),
            row.get('units'),
        ]

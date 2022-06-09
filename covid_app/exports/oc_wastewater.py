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
    'Units',
    '<- CAL3 | DWRL ->',
    'K-Virus 7d Avg',
    'Virus',
    'Virus (k)',
    'Rolling 10d Avg',
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
        cal3 = self.extract.cal3_samples.get(dated, {})
        dwrl = self.extract.dwrl_samples.get(dated, {})

        return [
            dated,
            self.extract.viral_counts_7d_avg.get(dated),
            cal3.get('virus'),
            cal3.get('virus_k'),
            cal3.get('log_virus'),
            cal3.get('Ten_Rollapply'),
            cal3.get('data_source'),
            cal3.get('Lab Id'),
            cal3.get('units'),
            '<-- CAL | DWR -->',
            dwrl.get('virus_7d_avg'),
            dwrl.get('virus'),
            dwrl.get('virus_k'),
            dwrl.get('Ten_Rollapply'),
            dwrl.get('units')
        ]

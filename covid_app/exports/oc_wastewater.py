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
    'Virus/ml 7d Avg',
    'Virus/ml',
    'Rolling 10d Avg',
    'Source',
    'Lab ID',
    'Virus',
    'Units',
    '<- CAL3 | DWRL ->',
    'Virus/ml 7d Avg',
    'Virus/ml',
    'Rolling 10d Avg',
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
                writer.writerow(self.extract_data_to_csv_row(dated))

        self.run_time_end = time.time()
        return self.csv_path

    #
    # Private
    #
    def extract_data_to_csv_row(self, dated):
        cal3 = self.extract.cal3_samples.get(dated, {})
        dwrl = self.extract.dwrl_samples.get(dated, {})
        divider = self.format_lab_row_divider(cal3, dwrl)

        return [
            dated,
            cal3.get('virus_ml_7d_avg'),
            cal3.get('virus_ml'),
            cal3.get('Ten Rollapply'),
            cal3.get('data_source'),
            cal3.get('Lab Id'),
            cal3.get('virus'),
            cal3.get('units'),
            divider,
            dwrl.get('virus_ml_7d_avg'),
            dwrl.get('virus_ml'),
            dwrl.get('Ten Rollapply'),
            dwrl.get('virus'),
            dwrl.get('units')
        ]

    def format_lab_row_divider(self, cal3, dwrl):
        divider_f = '{} {} {}'

        cal3_lab_id = cal3.get('Lab Id')
        dwrl_lab_id = dwrl.get('Lab Id')

        cal3_reported = cal3_lab_id is not None
        dwrl_reported = dwrl_lab_id is not None

        if cal3_reported and dwrl_reported:
            return divider_f.format(cal3_lab_id, '|', dwrl_lab_id)
        elif cal3_reported:
            return cal3_lab_id
        elif dwrl_reported:
            return dwrl_lab_id
        else:
            return ''

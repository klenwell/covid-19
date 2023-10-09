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
    'Virus/ml 7d Avg',
    'Virus/ml',
    'Lab ID',
    'Virus',
    'Units',
    '<- DP | LN ->',
    'Virus/ml 7d Avg',
    'Virus/ml',
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

    @cached_property
    def dana_point_samples(self):
        epa_id = 'CA0107417'
        return self.extract.samples_by_epa_id(epa_id)

    @cached_property
    def laguna_niguel_samples(self):
        epa_id = 'CA0107611'
        return self.extract.samples_by_epa_id(epa_id)

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
        sample1 = self.dana_point_samples.get(dated, {})
        sample2 = self.laguna_niguel_samples.get(dated, {})
        divider = self.format_lab_row_divider(sample1, sample2)

        return [
            dated,
            sample1.get('virus_ml_7d_avg'),
            sample1.get('virus_ml'),
            sample1.get('lab_id'),
            sample1.get('virus'),
            sample1.get('units'),
            divider,
            sample2.get('virus_ml_7d_avg'),
            sample2.get('virus_ml'),
            sample2.get('virus'),
            sample2.get('units')
        ]

    def format_lab_row_divider(self, sample1, sample2):
        divider_f = '{} {} {}'

        sample1_id = sample1.get('zipcode')
        sample2_id = sample2.get('zipcode')

        sample1_reported = sample1_id is not None
        sample2_reported = sample2_id is not None

        if sample1_reported and sample2_reported:
            return divider_f.format(sample1_id, '|', sample2_id)
        elif sample1_reported:
            return sample1_id
        elif sample2_reported:
            return sample2_id
        else:
            return ''

"""
OC August 2020 Test Analysis

For info on OC HCA data sources, see:
https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_pcr_csv/FeatureServer/0
"""
from os.path import join as path_join
from functools import cached_property
import csv
from datetime import date, timedelta

from config.app import DATA_ROOT


OC_DATA_PATH = path_join(DATA_ROOT, 'oc')
OC_ANALYTICS_DATA_PATH = path_join(OC_DATA_PATH, 'analytics')


class OcAugustTestAnalysis:
    #
    # Properties
    #
    @cached_property
    def start_date(self):
        return date(self.month, 1, self.year)

    @cached_property
    def dates(self):
        month_dates = []

        for n in range(self.days_in_month):
            dated = self.start_date + timedelta(days=n)
            month_dates.append(dated)

        return month_dates

    @cached_property
    def tests_time_series(self):
        pass

    @cached_property
    def positives_time_series(self):
        pass

    #
    # Instance Method
    #
    def __init__(self):
        self.month = 8
        self.year = 2020
        self.days_in_month = 31

    def extract_data(self):
        for dated in self.dates:
            # Extract data
            pass

            # Update test time series

            # Update positive time series

    def to_csv(self):
        pass

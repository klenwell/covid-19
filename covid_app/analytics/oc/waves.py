from os.path import join as path_join
from functools import cached_property
from datetime import timedelta
import time

from config.app import DATA_ROOT


#
# Constants
#



class OcWaveAnalysis:
    #
    # Properties
    #
    @property
    def positive_rates(self):
        return {}

    # Date sets
    @property
    def dates(self):
        return []

    # Etc
    @property
    def run_time(self):
        if not self.run_time_end:
            self.run_time_end = time.time()

        return self.run_time_end - self.run_time_start

    #
    # Instance Method
    #
    def __init__(self, test=False):
        self.run_time_start = time.time()
        self.run_time_end = None
        self.test = test

    #
    # Private
    #
    def compute_change(self, old, new):
        """Source: https://stackoverflow.com/q/30926840/1093087
        """
        return (new - old) / old * 100.0

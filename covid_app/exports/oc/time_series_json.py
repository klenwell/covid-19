from os.path import join as path_join
from functools import cached_property
from datetime import timedelta, datetime
import json

from config.app import GH_PAGES_ROOT
from covid_app.extracts.local.oc.daily_hca import OcDailyHcaExtract
from covid_app.extracts.local.oc.wastewater import OcWastewaterExtract

#
# Constants
#
JSON_DATA_PATH = path_join(GH_PAGES_ROOT, 'data', 'json', 'oc')
JSON_FILE_NAME = 'time-series.json'
DATE_OUT_F = '%Y-%m-%d'

# Wastewater Lab: CAL3 or DWRL
WASTEWATER_LAB = 'DWRL'

JSON_SCHEMA = {
    'meta': {},
    'dates': [],
    'max-values': {}
}

JSON_DATE_RECORD_SCHEMA = {
    'date': DATE_OUT_F,
    'wastewater': 0.0,
    'tests': 0.0,
    'positive-rate': 0.0,
    'cases': 0.0,
    'hospital-cases': 0.0,
    'icu-cases': 0.0,
    'deaths': 0.0
}


class OcTimeSeriesJsonExport:
    #
    # Properties
    #
    @property
    def json_path(self):
        return path_join(JSON_DATA_PATH, JSON_FILE_NAME)

    # Extracts
    @cached_property
    def waste_extract(self):
        return OcWastewaterExtract()

    @cached_property
    def case_extract(self):
        return OcDailyHcaExtract()

    # Export Data
    @cached_property
    def date_series(self):
        dated_series = []
        for dated in self.dates:
            record = {
                'date': dated.strftime(DATE_OUT_F),
                'wastewater': self.wastewater_7d_avg.get(dated),
                'tests': self.admin_tests_7d_avg.get(dated),
                'positive-rate': self.test_positive_rates.get(dated),
                'cases': self.case_extract.avg_new_cases.get(dated),
                'hospital-cases': self.hospital_cases_7d_avg.get(dated),
                'icu-cases': self.icu_cases_7d_avg.get(dated),
                'deaths': self.deaths_7d_avg.get(dated)
            }
            dated_series.append(record)
        return dated_series

    @cached_property
    def max_values(self):
        def series_values(key):
            return [r[key] for r in self.date_series if r[key] is not None]

        return {
            'wastewater': max(series_values('wastewater')),
            'tests': max(series_values('tests')),
            'positive-rate': max(series_values('positive-rate')),
            'cases': max(series_values('cases')),
            'hospital-cases': max(series_values('hospital-cases')),
            'icu-cases': max(series_values('icu-cases')),
            'deaths': max(series_values('deaths'))
        }

    @property
    def meta(self):
        return {
            'createdAt': self.iso_timestamp_now,
            'dataLastUpdated': self.end_date.strftime(DATE_OUT_F)
        }

    # Datasets
    @cached_property
    def wastewater_7d_avg(self):
        daily_values = {}
        default_dataset = self.waste_extract.dwrl
        lab = WASTEWATER_LAB.lower()
        dataset = getattr(self.waste_extract, lab, default_dataset)

        for dated in self.dates:
            lab = dataset.get(dated, {})
            daily_values[dated] = lab.get('avg_virus_7d')

        return daily_values

    @cached_property
    def test_positive_rates(self):
        daily_values = {}
        dataset = self.case_extract.avg_positive_rates

        for dated in self.dates:
            daily_values[dated] = dataset.get(dated)

        return daily_values

    @cached_property
    def admin_tests_7d_avg(self):
        daily_values = {}
        dataset = self.case_extract.tests_admin

        for dated in self.dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def positive_tests_7d_avg(self):
        daily_values = {}
        dataset = self.case_extract.tests_positive

        for dated in self.dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def hospital_cases_7d_avg(self):
        daily_values = {}
        dataset = self.case_extract.hospitalizations

        for dated in self.dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def icu_cases_7d_avg(self):
        daily_values = {}
        dataset = self.case_extract.icu_cases

        for dated in self.dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    @cached_property
    def deaths_7d_avg(self):
        daily_values = {}
        dataset = self.case_extract.deaths

        for dated in self.dates:
            week_avg = self.week_avg_from_date(dataset, dated)
            daily_values[dated] = week_avg

        return daily_values

    # Dates
    @property
    def dates(self):
        # Start on start_date (not first_date) and end on last_date (not end_date).
        start_index = self.case_extract.row_dates.index(self.case_extract.start_date)
        return self.case_extract.row_dates[start_index:]

    @property
    def start_date(self):
        return self.dates[0]

    @property
    def end_date(self):
        return self.dates[-1]

    @property
    def iso_timestamp_now(self):
        # Source: https://stackoverflow.com/a/28147286/1093087
        return datetime.now().astimezone().replace(microsecond=0).isoformat()

    #
    # Instance Method
    #
    def to_json_file(self):
        time_series = JSON_SCHEMA.copy()

        time_series['dates'] = self.date_series
        time_series['max-values'] = self.max_values
        time_series['meta'] = self.meta

        # pretty print
        with open(self.json_path, 'w') as f:
            f.write(json.dumps(time_series, indent=4))

        return self.json_path

    #
    # Private
    #
    def week_avg_from_date(self, daily_values, from_date):
        values = []
        for n in range(7):
            dated = from_date - timedelta(days=n)
            value = daily_values.get(dated)

            if value is None:
                return None

            values.append(value)
        return sum(values) / len(values)

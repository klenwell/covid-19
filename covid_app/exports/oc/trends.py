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
JSON_FILE_NAME = 'trends.json'
NUM_WEEKS = 5

# Wastewater Lab: CAL3 or DWRL
WASTEWATER_LAB = 'DWRL'

JSON_SCHEMA = {
    'weeks': [],
    'meta': {}
}

DATE_OUT_F = '%Y-%m-%d'


class OcTrendsExport:
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
    def weeks(self):
        weeks_data = []
        for n in range(NUM_WEEKS):
            trends_data = self.dated_trends[self.week_dates[n]]
            weeks_data.append(trends_data)
        return weeks_data

    @property
    def meta(self):
        return {
            'createdAt': self.iso_timestamp,
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
    def dated_trends(self):
        trends = {}
        for end_date in self.dates:
            trend = self.compute_trends(end_date)
            trends[end_date] = trend
        return trends

    # Dates
    @property
    def dates(self):
        num_dates = (NUM_WEEKS + 1) * 7
        return self.case_extract.dates[-num_dates:]

    @property
    def week_dates(self):
        week_dates = []
        most_recent_dates = sorted(self.dates, reverse=True)

        for n in range(5):
            offset = n * 7
            dated = most_recent_dates[offset]
            week_dates.append(dated)

        return week_dates

    @property
    def end_date(self):
        return self.dates[-1]

    @property
    def iso_timestamp(self):
        # Source: https://stackoverflow.com/a/28147286/1093087
        return datetime.now().astimezone().replace(microsecond=0).isoformat()

    #
    # Instance Method
    #
    def to_json_file(self):
        trends = JSON_SCHEMA.copy()

        trends['weeks'] = self.weeks
        trends['meta'] = self.meta

        # pretty print
        with open(self.json_path, 'w') as f:
            f.write(json.dumps(trends, indent=4))

        return self.json_path

    #
    # Private
    #
    def compute_trends(self, end_date):
        start_date = end_date - timedelta(days=6)
        compare_end_date = end_date - timedelta(days=7)
        compare_start_date = compare_end_date - timedelta(days=6)

        return {
            'startDate': start_date.strftime(DATE_OUT_F),
            'endDate': end_date.strftime(DATE_OUT_F),
            'testPositiveRate': {
                'value': self.test_positive_rates[end_date],
                'delta': self.compute_change(
                    self.test_positive_rates.get(compare_end_date),
                    self.test_positive_rates[end_date]
                )
            },
            'adminTests': {
                'average7d': self.admin_tests_7d_avg[end_date],
                'delta': self.compute_change(
                    self.admin_tests_7d_avg.get(compare_end_date),
                    self.admin_tests_7d_avg[end_date]
                )
            },
            'positiveTests': {
                'average7d': self.positive_tests_7d_avg[end_date],
                'delta': self.compute_change(
                    self.positive_tests_7d_avg.get(compare_end_date),
                    self.positive_tests_7d_avg[end_date]
                )
            },
            'wastewater': {
                'average7d': self.wastewater_7d_avg.get(end_date),
                'delta': self.compute_change(
                    self.wastewater_7d_avg.get(compare_end_date),
                    self.wastewater_7d_avg.get(end_date)
                )
            },
            'hospitalCases': {
                'average7d': self.hospital_cases_7d_avg[end_date],
                'delta': self.compute_change(
                    self.hospital_cases_7d_avg.get(compare_end_date),
                    self.hospital_cases_7d_avg[end_date]
                )
            },
            'deaths': {
                'total': self.sum_deaths(start_date, end_date),
                'delta': self.compute_change(
                    self.sum_deaths(compare_start_date, compare_end_date),
                    self.sum_deaths(start_date, end_date)
                )
            }
        }

    def sum_deaths(self, start_date, end_date):
        deaths = []
        days = (end_date - start_date).days

        for n in range(days+1):
            dated = start_date + timedelta(days=n)
            num_deaths = self.case_extract.deaths.get(dated, 0)
            deaths.append(num_deaths)

        return sum(deaths)

    def compute_change(self, old, new):
        """Source: https://stackoverflow.com/q/30926840/1093087
        """
        if not (old and new):
            return None
        return (new - old) / old * 100.0

    def week_avg_from_date(self, daily_values, from_date):
        values = []
        for n in range(7):
            dated = from_date - timedelta(days=n)
            value = daily_values[dated]
            values.append(value)
        return sum(values) / len(values)

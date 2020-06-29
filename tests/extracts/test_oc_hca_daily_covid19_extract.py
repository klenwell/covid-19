from datetime import datetime

from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.extracts.oc_hca.daily_covid19_extract import (
    DailyCovid19Extract, DailyCovid19ExtractV1, DailyCovid19ExtractV2)


class OcHcaDailyCovid19ExtractTest(AppTestCase):
    def test_expects_to_extract_data_for_version_2(self):
        # Arrange
        html_fname = 'oc-hca-dashboard-20200604.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        may_1 = datetime(2020, 5, 1).date()

        # Assume
        DailyCovid19ExtractV2.is_detected(html)

        # Act
        extract = DailyCovid19ExtractV2(html)

        # Assert
        self.assertEqual(str(extract.starts_on), '2020-02-01')
        self.assertEqual(str(extract.ends_on), '2020-06-04')
        self.assertEqual(len(extract.dates), 88)
        self.assertEqual(extract.new_cases[extract.ends_on], 107)
        self.assertEqual(extract.new_tests[may_1], 2830)
        self.assertEqual(extract.hospitalizations[may_1], 213)
        self.assertEqual(extract.icu_cases[may_1], 60)
        self.assertEqual(extract.VERSION, 2)

    def test_expects_to_extract_data_for_version_1(self):
        # Arrange
        html_fname = 'oc-hca-dashboard-archive-20200524.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        may_1 = datetime(2020, 5, 1).date()

        # Assume
        DailyCovid19ExtractV1.is_detected(html)

        # Act
        extract = DailyCovid19ExtractV1(html)

        # Assert
        self.assertEqual(str(extract.starts_on), '2020-02-01')
        self.assertEqual(str(extract.ends_on), '2020-05-23')
        self.assertEqual(len(extract.dates), 76)
        self.assertEqual(extract.new_cases[extract.ends_on], 216)
        self.assertEqual(extract.new_tests[may_1], 2763)
        self.assertEqual(extract.hospitalizations[may_1], 202)
        self.assertEqual(extract.icu_cases[may_1], 58)
        self.assertEqual(extract.VERSION, 1)

    def test_expects_to_detect_extract_version_2(self):
        # Arrange
        html_fname = 'oc-hca-dashboard-20200604.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        handler = DailyCovid19Extract()

        # Act
        Extract = handler.detect_archive_version(html)

        # Assert
        self.assertEqual(Extract.VERSION, 2)

    def test_expects_to_detect_extract_version_1(self):
        # Arrange
        html_fname = 'oc-hca-dashboard-archive-20200524.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        handler = DailyCovid19Extract()

        # Act
        Extract = handler.detect_archive_version(html)

        # Assert
        self.assertEqual(Extract.VERSION, 1)

    def test_expects_to_raise_error_when_extract_version_not_detected(self):
        # Arrange
        bad_source = 'Not found!'
        handler = DailyCovid19Extract()

        # Act
        with self.assertRaises(Exception) as context:
            handler.detect_archive_version(bad_source)

        # Assert
        self.assertEqual(str(context.exception), 'Valid extract source not detected.')

import requests_mock
from datetime import date
import re

from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.services.oc_health_service import OCHealthService
from covid_app.extracts.ny_times_covid19 import EXTRACT_URL as NY_TIMES_EXTRACT_URL
from covid_app.extracts.oc_hca.daily_covid19_extract import EXTRACT_URL as OC_HCA_EXTRACT_URL
from covid_app.extracts.covid19_projections import BASE_URL as PROJECTION_BASE_URL


class OrionAdvisorServiceTest(AppTestCase):
    def setUpOcHcaExtractMock(self, fname, webmock):
        html_path = path_join(FILES_ROOT, fname)
        webmock.get(OC_HCA_EXTRACT_URL, text=self.readFile(html_path))

    def setUpNyTimesExtractMock(self, webmock):
        mock_content = [
            'date,county,state,fips,cases,deaths',
            '2020-06-03,Orange,California,06059,6790,158'
        ]
        webmock.get(NY_TIMES_EXTRACT_URL, text="\n".join(mock_content))

    def setUpProjectionExtractMock(self, webmock):
        # See https://requests-mock.readthedocs.io/en/latest/matching.html#regular-expressions
        url_pattern = '{}/.*'.format(PROJECTION_BASE_URL)
        matcher = re.compile(url_pattern)
        html_fname = 'oc-projections-20200610.html'
        html_path = path_join(FILES_ROOT, html_fname)
        webmock.get(matcher, text=self.readFile(html_path))

    def test_expects_instance_of_service_class(self):
        # Act
        orion = OCHealthService()

        # Assert
        self.assertIsInstance(orion, OCHealthService)

    @requests_mock.mock()
    def test_expects_to_extract_daily_data_rows_from_archived_page(self, webmock):
        # Arrange
        service = OCHealthService()

        # Mock Web Services
        self.setUpOcHcaExtractMock('oc-hca-dashboard-archive-20200524.html', webmock)
        self.setUpNyTimesExtractMock(webmock)
        self.setUpProjectionExtractMock(webmock)

        # Expected Data
        expected_may_23_row = [date(2020, 5, 23), 216, '', '', '', '']
        expected_may_22_row = [date(2020, 5, 22), 108, 1033, 249, 101, '']

        # Act
        rows = service.extract_archive_data_rows()
        may_23_row_sans_rt = rows[-1][:6]
        may_22_row_sans_rt = rows[-2][:6]

        # Assert
        self.assertEqual(len(rows), 84)
        self.assertEqual(may_23_row_sans_rt, expected_may_23_row)
        self.assertEqual(may_22_row_sans_rt, expected_may_22_row)

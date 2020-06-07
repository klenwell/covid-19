import requests_mock
from datetime import date

from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.services.oc_health_service import OCHealthService
from covid_app.extracts.ny_times_covid19 import EXTRACT_URL as NY_TIMES_EXTRACT_URL
from covid_app.extracts.oc_hca.daily_covid19_extract import EXTRACT_URL as OC_HCA_EXTRACT_URL


class OrionAdvisorServiceTest(AppTestCase):
    def test_expects_instance_of_service_class(self):
        # Act
        orion = OCHealthService()

        # Assert
        self.assertIsInstance(orion, OCHealthService)

    @requests_mock.mock()
    def test_expects_to_extract_daily_data_rows_from_latest_version_of_page(self, webmock):
        # Arrange
        service = OCHealthService()
        html_fname = 'oc-hca-dashboard-20200604.html'
        html_path = path_join(FILES_ROOT, html_fname)
        expected_june_4_row = [date(2020, 6, 4), 107, '', '', '', '']
        expected_june_3_row = [date(2020, 6, 3), 137, 1658, '', '', 158]
        expected_june_2_row = [date(2020, 6, 2), 99, 2302, 293, 129, '']

        # Mock OC HCA service
        webmock.get(OC_HCA_EXTRACT_URL, text=self.readFile(html_path))

        # Mock NY Times service
        mock_content = [
            'date,county,state,fips,cases,deaths',
            '2020-06-03,Orange,California,06059,6790,158'
        ]
        webmock.get(NY_TIMES_EXTRACT_URL, text="\n".join(mock_content))

        # Act
        rows = service.extract_daily_data_rows()
        june_4_row = rows[-1]
        june_3_row = rows[-2]
        june_2_row = rows[-3]

        # Assert
        self.assertEqual(len(rows), 96)
        self.assertEqual(june_4_row, expected_june_4_row)
        self.assertEqual(june_3_row, expected_june_3_row)
        self.assertEqual(june_2_row, expected_june_2_row)

    @requests_mock.mock()
    def test_expects_to_extract_daily_data_rows_from_archived_page(self, webmock):
        # Arrange
        service = OCHealthService()
        html_fname = 'oc-hca-dashboard-archive-20200524.html'
        html_path = path_join(FILES_ROOT, html_fname)
        expected_may_23_row = [date(2020, 5, 23), 216, '', '', '', '']
        expected_may_22_row = [date(2020, 5, 22), 108, 1033, 249, 101, '']

        # Mock OC HCA service
        webmock.get(OC_HCA_EXTRACT_URL, text=self.readFile(html_path))

        # Mock NY Times service
        mock_content = [
            'date,county,state,fips,cases,deaths',
            '2020-06-03,Orange,California,06059,6790,158'
        ]
        webmock.get(NY_TIMES_EXTRACT_URL, text="\n".join(mock_content))

        # Act
        rows = service.extract_daily_data_rows()
        may_23_row = rows[-1]
        may_22_row = rows[-2]

        # Assert
        self.assertEqual(len(rows), 84)
        self.assertEqual(may_23_row, expected_may_23_row)
        self.assertEqual(may_22_row, expected_may_22_row)

import requests_mock
from datetime import date

from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.services.oc_health_service import OCHealthService
from covid_app.extracts.ny_times_covid19 import EXTRACT_URL as NY_TIMES_EXTRACT_URL
from covid_app.extracts.oc_hca.daily_covid19_extract import EXTRACT_URL as OC_HCA_EXTRACT_URL
from covid_app.extracts.covid19_projections import EXTRACT_URL as PROJECTION_EXTRACT_URL


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
        html_fname = 'oc-projections-20200610.html'
        html_path = path_join(FILES_ROOT, html_fname)
        webmock.get(PROJECTION_EXTRACT_URL, text=self.readFile(html_path))

    def test_expects_instance_of_service_class(self):
        # Act
        orion = OCHealthService()

        # Assert
        self.assertIsInstance(orion, OCHealthService)

    @requests_mock.mock()
    def test_expects_to_extract_daily_data_rows_from_latest_version_of_page(self, webmock):
        # Arrange
        service = OCHealthService()

        # Mock Web Services
        self.setUpOcHcaExtractMock('oc-hca-dashboard-20200604.html', webmock)
        self.setUpNyTimesExtractMock(webmock)
        self.setUpProjectionExtractMock(webmock)

        # Expected Data
        expected_june_4_row = [date(2020, 6, 4), 107, '', '', '', '']
        expected_june_3_row = [date(2020, 6, 3), 137, 1658, '', '', 158]
        expected_june_2_row = [date(2020, 6, 2), 99, 2302, 293, 129, '']

        # Act
        rows = service.extract_daily_data_rows()
        june_4_row_sans_rt = rows[-1][:6]
        june_3_row_sans_rt = rows[-2][:6]
        june_2_row_sans_rt = rows[-3][:6]
        june_4_rt = rows[-1][-1]

        # Assert
        self.assertEqual(len(rows), 96)
        self.assertEqual(june_4_row_sans_rt, expected_june_4_row)
        self.assertEqual(june_3_row_sans_rt, expected_june_3_row)
        self.assertEqual(june_2_row_sans_rt, expected_june_2_row)
        self.assertAlmostEqual(june_4_rt, 1.09, 2)

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
        rows = service.extract_daily_data_rows()
        may_23_row_sans_rt = rows[-1][:6]
        may_22_row_sans_rt = rows[-2][:6]

        # Assert
        self.assertEqual(len(rows), 84)
        self.assertEqual(may_23_row_sans_rt, expected_may_23_row)
        self.assertEqual(may_22_row_sans_rt, expected_may_22_row)

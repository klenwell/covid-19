from unittest.mock import MagicMock
from datetime import date

from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.services.oc_health_service import OCHealthService


class OrionAdvisorServiceTest(AppTestCase):
    def test_expects_instance_of_service_class(self):
        # Act
        orion = OCHealthService()

        # Assert
        self.assertIsInstance(orion, OCHealthService)

    def test_expects_to_extract_daily_data_rows_from_latest_version_of_page(self):
        # Arrange
        service = OCHealthService()
        html_fname = 'oc-hca-dashboard-20200604.html'
        html_path = path_join(FILES_ROOT, html_fname)
        expected_june_4_row = [date(2020, 6, 4), 107, '', '', '']
        expected_june_3_row = [date(2020, 6, 3), 137, 1658, '', '']
        expected_june_2_row = [date(2020, 6, 2), 99, 2302, 293, 129]

        # Mock fetch_page_source_method to return our test file
        with open(html_path, 'r') as f:
            html = f.read()
            service.fetch_page_source = MagicMock(return_value=html)

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
        self.assertEqual(service.format_version, 2)

    def test_expects_to_extract_daily_data_rows_from_archived_page(self):
        pass

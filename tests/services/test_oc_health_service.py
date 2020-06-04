from tests.helper import AppTestCase
from covid_app.services.oc_health_service import OCHealthService


class OrionAdvisorServiceTest(AppTestCase):
    def test_expects_instance_of_service_class(self):
        # Act
        orion = OCHealthService()

        # Assert
        self.assertIsInstance(orion, OCHealthService)

    def test_expects_to_extract_daily_data_rows_from_latest_version_of_page(self):
        pass

    def test_expects_to_extract_daily_data_rows_from_archived_page(self):
        pass

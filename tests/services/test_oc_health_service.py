from tests.helper import AppTestCase
from covid_app.services.oc_health_service import OCHealthService


class OrionAdvisorServiceTest(AppTestCase):
    def test_expects_instance_of_service_class(self):
        # Act
        orion = OCHealthService()

        # Assert
        self.assertIsInstance(orion, OCHealthService)

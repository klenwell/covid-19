from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.extracts.oc_hca.daily_covid19_extract import (
    DailyCovid19Extract, DailyCovid19ExtractV1, DailyCovid19ExtractV2)


class OcHcaDailyCovid19Extract(AppTestCase):
    def test_expects_to_detect_extract_version_2(self):
        # Arrange
        html_fname = 'oc-hca-dashboard-20200604.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        handler = DailyCovid19Extract()

        # Act
        Extract = handler.detect_version(html)

        # Assert
        self.assertEqual(Extract.VERSION, 2)

    def test_expects_to_detect_extract_version_1(self):
        # Arrange
        html_fname = 'oc-hca-dashboard-archive-20200524.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        handler = DailyCovid19Extract()

        # Act
        Extract = handler.detect_version(html)

        # Assert
        self.assertEqual(Extract.VERSION, 1)

    def test_expects_to_raise_error_when_extract_version_not_detected(self):
        pass

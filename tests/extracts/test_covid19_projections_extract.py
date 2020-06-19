from datetime import datetime

from tests.helper import AppTestCase, FILES_ROOT, path_join
from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract


class Covid19ProjectionsExtractTest(AppTestCase):
    def test_expects_to_extract_data_from_page_source(self):
        # Arrange
        html_fname = 'oc-projections-20200610.html'
        html_path = path_join(FILES_ROOT, html_fname)
        html = self.readFile(html_path)
        extract = Covid19ProjectionsExtract(None)
        june_1 = datetime(2020, 6, 1).date()

        # Act
        daily_values = extract.filter_rts(html)

        # Assert
        self.assertAlmostEqual(daily_values[june_1], 1.09, 2)

    def test_expects_to_raise_error_when_page_source_is_invalid(self):
        # Arrange
        bad_source = 'Not found!'
        extract = Covid19ProjectionsExtract(None)
        expected_error = 'not enough values to unpack (expected 2, got 1)'

        # Act
        with self.assertRaises(ValueError) as context:
            extract.filter_rts(bad_source)

        # Assert
        self.assertEqual(str(context.exception), expected_error)

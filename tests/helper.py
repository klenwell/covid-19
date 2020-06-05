from os.path import join as path_join, exists as path_exists
from unittest import TestCase
from pytest_socket import disable_socket
from cement import TestApp

from config.app import PROJECT_ROOT
from covid_app.main import CovidApp


#
# Constants
#
TEST_ROOT = path_join(PROJECT_ROOT, 'tests')
FILES_ROOT = path_join(TEST_ROOT, 'fixtures', 'files')


#
# Test App Class
#
class CovidAppTest(TestApp, CovidApp):
    """A sub-class of app class that is better suited for testing."""

    class Meta:
        label = 'covid_app'


#
# Project Test Class with Custom Asserts
#
class AppTestCase(TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        pass

    def assertPathExists(self, path):
        self.assertTrue(path_exists(path))

    def assertPathDoesNotExist(self, path):
        self.assertFalse(path_exists(path))

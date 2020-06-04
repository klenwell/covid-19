from os.path import exists as path_exists
from unittest import TestCase
from pytest_socket import disable_socket
from cement import TestApp
from covid_app.main import CovidApp


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

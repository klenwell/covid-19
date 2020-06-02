from cement import Controller
from cement import ex as expose
import requests
import json
import csv

from ..services.oc_health_service import OCHealthService


class BaseController(Controller):
    class Meta:
        label = 'base'

    # python app.py new-tests
    @expose(help="Outputs csv file with OC HCA test counts.")
    def new_tests(self):
        csv_file = 'new_tests.csv'
        header_row = ['Date', 'Count']
        service = OCHealthService()
        new_tests = service.extract_new_tests()
        sorted_tests = sorted(new_tests, key=lambda t: t[0], reverse=True)

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header_row)
            for row in sorted_tests:
                writer.writerow(row)

        print('CSV written to {}'.format(csv_file))

    # python app.py new-cases
    @expose(help="Outputs csv file with OC HCA case counts.")
    def new_cases(self):
        csv_file = 'new_cases.csv'
        header_row = ['Date', 'Count']
        service = OCHealthService()
        new_cases = service.extract_new_cases()
        sorted_cases = sorted(new_cases, key=lambda t: t[0], reverse=True)

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header_row)
            for row in sorted_cases:
                writer.writerow(row)

        print('CSV written to {}'.format(csv_file))

    # python app.py interactive
    @expose(help="Run the Application interactively.")
    def interactive(self):
        csv_file = 'new_tests.csv'
        header_row = ['Date', 'Count']
        service = OCHealthService()
        new_tests = service.extract_new_tests()
        sorted_tests = sorted(new_tests, key=lambda t: t[0], reverse=True)
        breakpoint()

    # python app.py test -f foo arg1 extra2 extra2
    @expose(
        help="Test Cement framework and CLI.",
        arguments=[
            (['-f', '--foo'], dict(action='store', help='the notorious foo')),

            # https://github.com/datafolklabs/cement/issues/256
            (['arg1'], dict(action='store', nargs=1)),
            (['extras'], dict(action='store', nargs='*'))
        ]
    )
    def test(self):
        data = {'args': self.app.pargs}
        self.app.render(data, 'test.jinja2')

from cement import Controller
from cement import ex as expose


from ..services.mi_health_service import MiHealthService
from ..services.us_health_service import USHealthService


class BaseController(Controller):
    class Meta:
        label = 'base'

    # python app.py kent-daily
    @expose(help="Export Kent County data to csv file.")
    def kent_daily(self):
        result = MiHealthService.export_daily_kent_csv()
        print(result)

    # python app.py us-daily
    @expose(help="Export US data to csv file.")
    def us_daily(self):
        result = USHealthService.export_daily_csv()
        print(result)

    # python app.py interactive
    # This command can be used for testing and development.
    @expose(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        service = MiHealthService()
        extract = service.us_gov_extract
        json_data = extract.daily_kent_json_data
        print(json_data.keys())

        results_data = json_data['results'][0]['result']['data']
        test_data = results_data['dsr']['DS'][0]['PH'][0]['DM0'][1:]
        last_report = test_data[-1]
        date = extract.timestamp_to_date(last_report['G0'])
        viral_tests = last_report['X'][0]['M0']

        print({date: viral_tests})
        breakpoint()

    # python app.py test -f foo arg1 extra1 extra2
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
        vars = {'args': self.app.pargs}
        self.app.render(vars, 'test.jinja2')

from cement import Controller
from cement import ex as expose


from ..services.oc_health_service import OCHealthService


class BaseController(Controller):
    class Meta:
        label = 'base'

    # python app.py oc-daily
    @expose(help="Export data from OC HCA site to csv file.")
    def oc_daily(self):
        csv = OCHealthService.export_daily_csv()
        vars = {'csv': csv}
        self.app.render(vars, 'oc_daily.jinja2')

    # python app.py interactive
    # This command can be used for testing and development.
    @expose(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        service = OCHealthService()
        html = service.fetch_page_source()
        new_cases = service.extract_new_cases(html)
        latest_date = service.extract_latest_date_from_new_cases(new_cases)
        print(latest_date)
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

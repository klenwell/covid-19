from cement import Controller
from cement import ex as expose


from ..services.oc_health_service import OCHealthService
from ..services.mi_health_service import MiHealthService
from ..services.us_health_service import USHealthService


class BaseController(Controller):
    class Meta:
        label = 'base'

    # python app.py oc-daily
    @expose(
        help="Export data from OC HCA site to csv file.",
        arguments=[
            (['-a'], dict(dest='archive', action='store',
                          help='Extract data from provided URL for archived web page.'))
        ]
    )
    def oc_daily(self):
        archive_url = self.app.pargs.archive

        if archive_url:
            csv = OCHealthService.export_archive(archive_url)
        else:
            csv = OCHealthService.export_daily_csv()

        vars = {'csv': csv}
        self.app.render(vars, 'oc_daily.jinja2')

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
        from covid_app.models.oc_daily_log import OcDailyLog
        logs = OcDailyLog.all()
        print(len(logs))
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

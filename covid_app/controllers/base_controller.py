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
    @expose(
        help="Run the Application interactively. Useful for testing and development.",
        arguments=[
            (['-a'], dict(dest='archive', action='store',
                          help='Extract data from archived web page.'))
        ]
    )
    def interactive(self):
        url = None
        use_archive = self.app.pargs.archive
        if use_archive:
            url = '{}/{}'.format('https://web.archive.org/web/20200331224552',
                                 'https://occovid19.ochealthinfo.com/coronavirus-in-oc')
            print('Using archive ({}): {}'.format(self.app.pargs.archive, format(url)))
        data = OCHealthService.fetch_daily_data(url)
        print('Latest daily report: {}'.format(data[-1]))
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

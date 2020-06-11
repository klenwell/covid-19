from cement import Controller
from cement import ex as expose


from ..services.oc_health_service import OCHealthService
from ..services.mi_health_service import MiHealthService


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
    @expose(help="Export MI-6 data from NY Times repo to csv file.")
    def kent_daily(self):
        result = MiHealthService.export_daily_kent_csv()
        print(result)

    # python app.py interactive
    # This command can be used for testing and development.
    @expose(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        from os import path
        from config.app import PROJECT_ROOT
        import json

        path = path.join(PROJECT_ROOT, 'tests/fixtures/files/oc-projections-20200610.html')

        with open(path, 'r') as f:
            html = f.read()

        _, tail = html.split('Plotly.newPlot', 1)
        _, tail = tail.split('[', 1)
        head, _ = tail.split("\n", 1)
        data, _ = head.rsplit(']', 1)
        data = '[{}]'.format(data)
        plot_data = json.loads(data)
        rt_data = plot_data[-1]

        rt = [(rt_data['x'][n], rt_data['y'][n]) for n in range(len(rt_data['x']))]

        print(rt)
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

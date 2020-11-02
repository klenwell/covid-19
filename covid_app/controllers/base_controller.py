from config.app import DATA_ROOT
from os.path import join as path_join

from cement import Controller
from cement import ex as expose

from ..services.mi_health_service import MiHealthService
from ..services.us_health_service import USHealthService
from ..extracts.san_diego_county import SanDiegoCountyDailyExtract


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

    # python app.py sd-daily
    @expose(help="Export San Diego data to csv file.")
    def sd_daily(self):
        file_name = 'sd-county-daily-export.csv'
        csv_path = path_join(DATA_ROOT, 'ca', file_name)

        extract = SanDiegoCountyDailyExtract()
        csv_path = extract.to_csv(csv_path)
        print(csv_path)

    # python app.py interactive
    # This command can be used for testing and development.
    @expose(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        from covid_app.extracts.covid19_projections import Covid19ProjectionsExtract, BASE_URL
        from urllib.parse import urljoin
        import json

        url_path = 'us-ca-orange'
        url = urljoin(BASE_URL, url_path)

        extract = Covid19ProjectionsExtract(url)
        html = extract.fetch_data_source()

        # Need to fix this to snip at right spot.
        data_str = extract.extract_json_data_from_embedded_js(html)

        plot_data = json.loads(data_str)
        rt_data = plot_data[-1]

        print(rt_data['x'][-40], rt_data['y'][-40])
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

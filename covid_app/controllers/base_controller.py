from config.app import DATA_ROOT
from os.path import join as path_join

from cement import Controller
from cement import ex as expose

from covid_app.services.mi_health_service import MiHealthService
from covid_app.extracts.san_diego_county import SanDiegoCountyDailyExtract
from covid_app.exports.us_daily_covid import USDailyCovidExport


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
        export = USDailyCovidExport()
        result = export.to_csv()
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
        from covid_app.extracts.cdc.us_county_timeseries_extract \
            import CdcCountyTimeseriesExtract, KENT_FIPS, TIMESERIES_DATA_KEY

        extract = CdcCountyTimeseriesExtract(fips=KENT_FIPS)
        print(extract.url)
        print(extract.fips)
        print(extract.county_id)

        json_data = extract.fetch_data_source()

        timeseries_data = json_data[TIMESERIES_DATA_KEY]
        print(len(timeseries_data))
        print(timeseries_data[100])

        print(extract.starts_on, extract.ends_on)
        print(extract.daily_logs[extract.ends_on])

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

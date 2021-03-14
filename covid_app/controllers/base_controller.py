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
        from sodapy import Socrata
        from datetime import date, datetime

        # https://dev.socrata.com/foundry/healthdata.gov/j8mb-icvb
        dataset_id = 'j8mb-icvb'
        start_date = date(2021,3,5)
        start_date_iso = datetime.combine(start_date, datetime.min.time()).isoformat()
        parameters = {
            'date': start_date_iso
            #'$where': "date >= '{}'".format(start_date_iso),
        }
        print(parameters)

        # https://github.com/xmunoz/sodapy
        to_int = lambda s: int(float(s))
        client = Socrata("sandbox.demo.socrata.com", None)
        data = client.get(dataset_id, **parameters)
        positives = [to_int(d['new_results_reported']) for d in data if d['overall_outcome'] == 'Positive']
        negatives = [to_int(d['new_results_reported']) for d in data if d['overall_outcome'] == 'Negative']
        blanks = [to_int(d['new_results_reported']) for d in data if d['overall_outcome'] == 'Inconclusive']
        print([d for d in data if d['state'] == 'AL'])
        print({
            'date': datetime.fromisoformat(data[0]['date']).date(),
            'rows': len(data),
            'positives': sum(positives),
            'negatives': sum(negatives),
            'inconclusives': sum(blanks),
            'total': sum(positives) + sum(negatives)
        })


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

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

        # https://dev.socrata.com/foundry/healthdata.gov/g62h-syeh
        dataset_id = 'g62h-syeh'
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
        hospitalized = 'total_adult_patients_hospitalized_confirmed_and_suspected_covid'
        icued = 'staffed_icu_adult_patients_confirmed_and_suspected_covid'
        hospital_cases = [to_int(d[hospitalized]) for d in data]
        icu_cases = [to_int(d[icued]) for d in data]
        print([d for d in data if d['state'] == 'CA'])
        print({
            'date': datetime.fromisoformat(data[0]['date']).date(),
            'rows': len(data),
            'hospital_cases': sum(hospital_cases),
            'icu_cases': sum(icu_cases)
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

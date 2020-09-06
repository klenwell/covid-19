from datetime import date
from cement import Controller
from cement import ex as expose

from covid_app.services.oc_health_service import OCHealthService
from covid_app.analytics.oc_by_day import OcByDayAnalysis
from covid_app.analytics.oc_testing import OcTestingAnalysis
from covid_app.analytics.oc_hospitalizations import OcHospitalizationsAnalysis
from covid_app.analytics.oc_summer_surge import OcSummerSurgeAnalysis
from covid_app.analytics.oc_august_testing import OcAugustTestAnalysis


class OcController(Controller):
    class Meta:
        label = 'oc'
        stacked_on = 'base'
        stacked_type = 'nested'

    # python app.py oc daily
    @expose(help="Export data from OC HCA site to csv file.")
    def daily(self):
        service = OCHealthService.export_daily_csv()
        vars = {'service': service}
        self.app.render(vars, 'oc/daily.jinja2')

    # python app.py oc archive -a https://web.archive.org/web/20200503202327/https://occovid19.ochealthinfo.com/coronavirus-in-oc # noqa: E501
    @expose(
        help="Export data from archived version of OC HCA site to csv file.",
        arguments=[
            (['-a'], dict(dest='archive', action='store', help='URL for archived web page.'))
        ]
    )
    def archive(self):
        archive_url = self.app.pargs.archive
        csv = OCHealthService.export_archive(archive_url)
        vars = {'csv': csv}
        self.app.render(vars, 'oc_daily.jinja2')

    # python app.py oc analyze-by-day
    @expose(help="Generate analysis of OC HCA data by day-of-week.")
    def analyze_by_day(self):
        start_on = date(2020, 4, 26)
        end_on = date(2020, 6, 20)

        report = OcByDayAnalysis()
        report.analyze_dates(start_on, end_on)
        csv = report.to_csv()
        print('CSV path: {}'.format(csv))

        for day in report.days:
            print(report.data_to_csv_row(day))

    # python app.py oc analyze-test-delays
    @expose(help="Analyze testing delays based on data.")
    def analyze_test_delays(self):
        # Generate CSV
        analysis = OcTestingAnalysis()
        ordered_tests = analysis.dated_virus_tests
        csv_path = analysis.to_csv()

        # Render view
        vars = {
            'csv_path': csv_path,
            'num_tests': len(ordered_tests),
            'analysis': analysis
        }
        self.app.render(vars, 'oc/test-delays-analysis.jinja2')

    # python app.py oc analyze-hospitalizations
    @expose(help="Analyze hospitalizations based on data.")
    def analyze_hospitalizations(self):
        # Generate CSV
        analysis = OcHospitalizationsAnalysis()
        csv_path = analysis.to_csv()

        # Render view
        vars = {
            'csv_path': csv_path,
            'analysis': analysis
        }
        print(vars)

    # python app.py oc analyze-surge
    @expose(help="Analyze hospitalizations based on data.")
    def analyze_surge(self):
        # Generate CSV
        analysis = OcSummerSurgeAnalysis()
        csv_path = analysis.to_csv()

        # Render view
        vars = {
            'csv_path': csv_path,
            'analysis': analysis
        }
        print(vars)

    # python app.py oc analyze-aug-tests
    @expose(help="Analyze test patterns in OC for August 2020.")
    def analyze_aug_tests(self):
        # Generate CSV
        analysis = OcAugustTestAnalysis()
        csv_path = analysis.to_csv()

        # Render view
        vars = {
            'csv_path': csv_path,
            'analysis': analysis
        }
        print(vars)

    # python app.py oc dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        from datetime import date
        aug_15 = date(2020, 8, 15)

        analysis = OcAugustTestAnalysis()
        aug_15_extract = analysis.daily_extracts[aug_15]
        print(aug_15_extract.admin_tests)
        print(analysis.total_tests_time_series[aug_15])
        breakpoint()

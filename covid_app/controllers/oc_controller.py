from datetime import date
from cement import Controller
from cement import ex as expose
from pprint import pformat

from covid_app.exports.oc_daily_data import OcDailyDataExport
from covid_app.exports.oc_daily_testing import OcDailyTestsExport
from covid_app.exports.oc_immunity import OCImmunityExport
from covid_app.exports.oc_wastewater import OCWastewaterExport
from covid_app.exports.oc.metrics import OCMetricsExport
from covid_app.exports.oc.waves import OCWavesExport
from covid_app.exports.oc.phases import OCPhasesExport
from covid_app.services.oc_health_service import OCHealthService

from covid_app.analytics.oc_by_day import OcByDayAnalysis
from covid_app.analytics.oc_testing import OcTestingAnalysis
from covid_app.analytics.oc_hospitalizations import OcHospitalizationsAnalysis
from covid_app.analytics.oc_vs_sd_analysis import OrangeCoVsSanDiegoAnalysis
from covid_app.analytics.oc_summer_surge import OcSummerSurgeAnalysis
from covid_app.analytics.oc_august_testing import OcAugustTestAnalysis
from covid_app.analytics.oc_monthly_testing import OcMonthlyTestAnalysis
from covid_app.analytics.oc_daily_testing import OcDailyTestingAnalysis


class OcController(Controller):
    class Meta:
        label = 'oc'
        stacked_on = 'base'
        stacked_type = 'nested'

    #
    # Daily Commands
    #
    # python app.py oc daily-v2
    @expose(help="Export latest daily data from OC HCA site.")
    def daily_v2(self):
        daily = OcDailyDataExport()
        daily.to_csv()

        immunity = OCImmunityExport()
        immunity.to_csv()

        vars = {
            'daily': daily,
            'immunity': immunity,
            'latest': immunity.estimates[-1]
        }
        self.app.render(vars, 'oc/daily-v2.jinja2')

    # python app.py oc daily
    @expose(help="Export data from OC HCA site to csv file.")
    def daily(self):
        service = OCHealthService.export_daily_csv()
        vars = {'service': service}
        self.app.render(vars, 'oc/daily.jinja2')

    # python app.py oc daily-tests
    @expose(help="Export daily OC HCA testing data to csv file.")
    def daily_tests(self):
        export = OcDailyTestsExport()
        export.to_csv()
        vars = {'export': export}
        self.app.render(vars, 'oc/daily-tests.jinja2')

    # python app.py oc immunity
    @expose(help="Export immunity projections to csv file.")
    def immunity(self):
        export = OCImmunityExport()
        export.to_csv()
        vars = {
            'export': export,
            'latest': export.estimates[-1]
        }
        self.app.render(vars, 'oc/immunity.jinja2')

    # python app.py oc wastewater [--mock]
    @expose(
        help="Export wastewater data to csv file.",
        arguments=[
            (['--mock'], dict(action='store_true', help='mock data using sample file'))
        ]
    )
    def wastewater(self):
        use_mock = self.app.pargs.mock
        export = OCWastewaterExport(mock=use_mock)
        export.to_csv()
        vars = {
            'export': export,
        }
        self.app.render(vars, 'oc/wastewater.jinja2')

    #
    # API / JSON Files
    #
    # python app.py oc metrics-json-file
    @expose(help="Output JSON file to docs/data/json/oc/metrics.json.")
    def metrics_json_file(self):
        export = OCMetricsExport(test=False)
        json_path = export.to_json_file()

        vars = {
            'json_path': json_path,
            'notes': [
                'Latest case update: {}'.format(export.latest_case_update),
                'Latest positive rate update: {}'.format(export.latest_test_update),
                'Latest wastewater update: {}'.format(export.latest_wastewater_update),
                'Run time: {} s'.format(round(export.run_time, 2))
            ]
        }
        self.app.render(vars, 'oc/json-export.jinja2')

    # python app.py oc waves-json-file
    @expose(help="Output JSON file to docs/data/json/oc/waves.json.")
    def waves_json_file(self):
        export = OCWavesExport(test=False)
        waves_json_path = export.waves_to_json_file()

        wave_count = len(export.analysis.epidemic.waves)
        smoothed_phase_count = len(export.analysis.epidemic.smoothed_phases)
        phase_count = len(export.analysis.epidemic.phases)
        waves = pformat(export.analysis.epidemic.waves)

        vars = {
            'json_path': waves_json_path,
            'notes': [
                'Data Source: {}'.format(export.data_source_path),
                'Total Waves: {}'.format(wave_count),
                'Total Smoothed Phases: {}'.format(smoothed_phase_count),
                'Total Phases: {}'.format(phase_count),
                'Run time: {} s'.format(round(export.run_time, 2)),
                'Waves:\n{}'.format(waves)
            ]
        }
        self.app.render(vars, 'oc/json-export.jinja2')

    # python app.py oc phases-json-file
    @expose(help="Output JSON file to docs/data/json/oc/phases.json.")
    def phases_json_file(self):
        export = OCPhasesExport(test=False)
        json_path = export.to_json_file()

        vars = {
            'json_path': json_path,
            'notes': [
                'Data Source: {}'.format(export.data_source_path),
                'Total Phases: {}'.format(len(export.phases)),
                'Run time: {} s'.format(round(export.run_time, 2)),
            ]
        }
        self.app.render(vars, 'oc/json-export.jinja2')

    #
    # Analytics
    #
    # python app.py oc analyze-daily-tests YEAR MONTH
    @expose(
        help="Analyze test patterns in OC for given month year.",
        arguments=[
            (['year'], dict(action='store')),
            (['month'], dict(action='store'))
        ]
    )
    def analyze_daily_tests(self):
        # Command Line Arguments
        year = int(self.app.pargs.year)
        month = int(self.app.pargs.month)

        analysis = OcDailyTestingAnalysis(year, month)
        csv_path = analysis.to_csv()

        # Render view
        vars = {
            'csv_path': csv_path,
            'analysis': analysis
        }
        self.app.render(vars, 'oc/daily-testing-analysis.jinja2')

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

    # python app.py oc vs-sd
    @expose(
        aliases=['vs-sd'],
        help="Analyze hospitalizations based on data.")
    def compare_san_diego_county(self):
        analysis = OrangeCoVsSanDiegoAnalysis()
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

    # python app.py oc analyze-monthly-tests YEAR MONTH
    @expose(
        help="Analyze test patterns in OC for given month year.",
        arguments=[
            (['year'], dict(action='store')),
            (['month'], dict(action='store'))
        ]
    )
    def analyze_monthly_tests(self):
        # Generate CSV
        year = int(self.app.pargs.year)
        month = int(self.app.pargs.month)

        analysis = OcMonthlyTestAnalysis(year, month)
        csv_path = analysis.to_csv()

        # Render view
        vars = {
            'csv_path': csv_path,
            'analysis': analysis
        }
        self.app.render(vars, 'oc/monthly-tests-analysis.jinja2')

    #
    # Other Commands
    #
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

    # python app.py oc dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        from covid_app.exports.oc.trends import OcTrendsExport
        from pprint import pprint

        export = OcTrendsExport()
        extract = export.case_extract
        print(export.week_dates)
        print(export.wastewater_7d_avg)
        pprint(export.weeks)
        breakpoint()

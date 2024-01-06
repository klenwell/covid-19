from datetime import date
from cement import Controller
from cement import ex as expose
from pprint import pformat

from covid_app.exports.oc_daily_data import OcDailyDataExport
from covid_app.exports.oc_daily_testing import OcDailyTestsExport
from covid_app.exports.oc.infections import OcInfectionsExport
from covid_app.exports.oc_immunity import OCImmunityExport
from covid_app.exports.oc_wastewater import OCWastewaterExport
from covid_app.exports.oc.metrics import OCMetricsExport
from covid_app.exports.oc.waves import OCWavesExport
from covid_app.exports.oc.phases import OCPhasesExport
from covid_app.exports.oc.trends import OcTrendsExport
from covid_app.exports.oc.historical import OcHistoricalExport
from covid_app.exports.oc.time_series_json import OcTimeSeriesJsonExport

from covid_app.analytics.oc_by_day import OcByDayAnalysis
from covid_app.analytics.oc_testing import OcTestingAnalysis
from covid_app.analytics.oc_august_testing import OcAugustTestAnalysis
from covid_app.analytics.oc_monthly_testing import OcMonthlyTestAnalysis
from covid_app.analytics.oc_daily_testing import OcDailyTestingAnalysis


class OcController(Controller):
    class Meta:
        label = 'oc'
        stacked_on = 'base'
        stacked_type = 'nested'

    #
    # Primary Interface
    #
    # python app.py oc infections
    @expose(help="Export infections data to data csv file.")
    def infections(self):
        export = OcInfectionsExport()
        csv_path = export.to_csv_file()
        vars = {
            'csv_path': csv_path,
            'notes': [
                'Start Date: {}'.format(export.starts_on),
                'End Date: {}'.format(export.ends_on),
                'Rows: {}'.format(len(export.dates)),
                'Run time: {} s'.format(round(export.run_time, 2))
            ]
        }
        self.app.render(vars, 'oc/csv-export.jinja2')

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
        phases = pformat(export.analysis.epidemic.smoothed_phases)

        vars = {
            'json_path': json_path,
            'notes': [
                'Data Source: {}'.format(export.data_source_path),
                'Total Phases: {}'.format(len(export.phases)),
                'Phases:\n{}'.format(pformat(export.analysis.epidemic.phases)),
                'Smoothed Phases:\n{}'.format(phases),
                'Run time: {} s'.format(round(export.run_time, 2))
            ]
        }
        self.app.render(vars, 'oc/json-export.jinja2')

    # python app.py oc trends-json-file
    @expose(help="Output JSON file to docs/data/json/oc/trends.json.")
    def trends_json_file(self):
        export = OcTrendsExport()
        json_path = export.to_json_file()

        vars = {
            'json_path': json_path,
            'notes': [
                'Start Date: {}'.format(export.weeks[0]['startDate']),
                'End Date: {}'.format(export.weeks[0]['endDate']),
            ]
        }
        self.app.render(vars, 'oc/json-export.jinja2')

    # python app.py oc time-series-json-file
    @expose(help="Output JSON file to docs/data/json/oc/time-series.json.")
    def time_series_json_file(self):
        export = OcTimeSeriesJsonExport()
        json_path = export.to_json_file()

        vars = {
            'json_path': json_path,
            'notes': [
                'Start Date: {}'.format(export.start_date),
                'End Date: {}'.format(export.end_date),
            ]
        }
        self.app.render(vars, 'oc/json-export.jinja2')

    #
    # Deprecated Commands
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

    # python app.py oc nightly
    @expose(help="Export data from OC HCA site to csv file.")
    def nightly(self):
        export = OcHistoricalExport()
        csv_path = export.to_csv_file()
        vars = {
            'csv_path': csv_path,
            'notes': [
                'Start Date: {}'.format(export.extract.starts_on),
                'End Date: {}'.format(export.extract.ends_on),
                'Rows: {}'.format(len(export.extract.dates)),
                'Run time: {} s'.format(round(export.run_time, 2))
            ]
        }
        self.app.render(vars, 'oc/csv-export.jinja2')

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
    # python app.py oc dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        from covid_app.extracts.cdph.oc_detailed_wastewater_extract import OcWastewaterExtract
        from pprint import pprint

        extract = OcWastewaterExtract(mock=True)

        print(extract.sample_csv_path)
        print(extract.zip_codes)
        pprint(extract.sites)

        breakpoint()

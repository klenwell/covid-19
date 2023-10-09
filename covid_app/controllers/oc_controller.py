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
        #breakpoint()
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
        from covid_app.extracts.cdph.oc_detailed_wastewater_extract import OcWastewaterExtract, DATA_ROOT
        from pprint import pprint
        from os.path import join

        OC_ZIPS = [92656, 92698, 92801, 92802, 92803, 92804, 92805, 92806, 92807, 92808,
            92809, 92812, 92814, 92815, 92816, 92817, 92825, 92850, 92899, 92811, 92821,
            92822, 92823, 90620, 90621, 90622, 90624, 92624, 92625, 92626, 92627, 92628,
            90630, 92629, 92650, 92609, 92610, 92708, 92728, 92831, 92832, 92833, 92834,
            92835, 92836, 92837, 92838, 92840, 92841, 92842, 92843, 92844, 92845, 92846,
            92605, 92615, 92646, 92647, 92648, 92649, 92602, 92603, 92604, 92606, 92612,
            92614, 92616, 92618, 92619, 92620, 92623, 92697, 92709, 92710, 90631, 90632,
            90633, 90623, 92694, 92651, 92652, 92637, 92653, 92654, 92607, 92677, 92630,
            90720, 90721, 92655, 92690, 92691, 92692, 92658, 92659, 92660, 92661, 92662,
            92663, 92657, 92856, 92857, 92859, 92862, 92863, 92864, 92865, 92866, 92867,
            92868, 92869, 92870, 92871, 92688, 92672, 92673, 92674, 92675, 92693, 92701,
            92702, 92703, 92704, 92705, 92706, 92707, 92711, 92712, 92725, 92735, 92799,
            90740, 92676, 90680, 90742, 90743, 92678, 92679, 92780, 92781, 92782, 92861,
            92683, 92684, 92685, 92885, 92886, 92887]
        oc_zip_set = set([str(zip) for zip in OC_ZIPS])

        dp_epa_id = 'CA0107417'
        ln_epa_id = 'CA0107611'

        extract = OcWastewaterExtract(mock=True)
        dp_samples = extract.samples_by_epa_id(dp_epa_id)
        ln_samples = extract.samples_by_epa_id(ln_epa_id)
        dp_rows = extract.rows_by_epa_id(dp_epa_id)
        ln_rows = extract.rows_by_epa_id(ln_epa_id)

        print(extract.sample_csv_path)
        print(oc_zip_set.intersection(extract.zip_codes))
        print(len(dp_samples))
        print(len(ln_samples))

        def show_me(row):
            headers = ['zipcode', 'wwtp_name', 'facility_name', 'sample_collect_date', 'lab_id', 'sample_id', 'site_id', 'epaid']
            return [row[header] for header in headers]

        old_cdph_csv = join(DATA_ROOT, 'samples/cdph-master-wastewater-20220726.csv')
        extract_v1 = OcWastewaterExtract(mock=True, csv_path=old_cdph_csv)
        print(extract_v1.sample_csv_path)
        print(len(extract_v1.csv_rows))
        print(oc_zip_set.intersection(extract_v1.zip_codes))
        print(len(extract.rows_by_zip('92708')))

        breakpoint()

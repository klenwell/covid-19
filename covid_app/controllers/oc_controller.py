from datetime import date
from cement import Controller
from cement import ex as expose

from covid_app.services.oc_health_service import OCHealthService
from covid_app.analytics.oc_by_day import OcByDayAnalysis
from covid_app.analytics.oc_testing import OcTestingAnalysis


class OcController(Controller):
    class Meta:
        label = 'oc'
        stacked_on = 'base'
        stacked_type = 'nested'

    # python app.py oc daily
    @expose(help="Export data from OC HCA site to csv file.")
    def daily(self):
        csv = OCHealthService.export_daily_csv()
        vars = {'csv': csv}
        self.app.render(vars, 'oc_daily.jinja2')

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

    # python app.py oc dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        from covid_app.extracts.unacast_social_distancing import UnacastSocialDistancingExtract

        extract = UnacastSocialDistancingExtract.oc()
        extract.fail_fast()
        daily_logs = extract.daily_logs
        daily_log = list(daily_logs.values())[0]

        print(len(daily_logs))
        print(daily_log.keys())
        print(daily_log)

        breakpoint()

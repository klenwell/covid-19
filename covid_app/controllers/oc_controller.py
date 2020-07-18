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
        from collections import Counter

        analysis = OcTestingAnalysis()
        ordered_tests = analysis.dated_virus_tests
        csv_path = analysis.to_csv()

        # Analyze
        wait_times = [t.days_to_report for t in ordered_tests]
        avg_wait = sum(wait_times) / len(wait_times)

        # Dump
        print('virus_tests: {}'.format(len(ordered_tests)))
        print('avg_wait: {}'.format(avg_wait))
        print('wait_times_freq: {}'.format(Counter(wait_times)))
        print('Analysis: {}'.format(csv_path))

    # python app.py oc dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        from ..extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3
        print(DailyCovid19ExtractV3.is_detected())

        extract = DailyCovid19ExtractV3()
        print(len(extract.daily_case_logs))

        from datetime import date, timedelta
        today = date.today()
        yesterday = today - timedelta(days=1)

        print({
            'today': extract.by_date(today),
            'yesterday': extract.by_date(yesterday)
        })

        print(len(extract.daily_case_logs))
        print(len(extract.daily_test_logs))

        breakpoint()

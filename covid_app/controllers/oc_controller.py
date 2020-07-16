from datetime import date
from cement import Controller
from cement import ex as expose

from covid_app.services.oc_health_service import OCHealthService
from covid_app.analytics.oc_by_day import OcByDayAnalysis


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
        import queue
        from math import floor
        from covid_app.models.oc.covid_virus_test import CovidVirusTest
        from ..extracts.oc_hca.versions.daily_covid19_extract_v3 import DailyCovid19ExtractV3

        extract = DailyCovid19ExtractV3()

        # Control for multiple positive tests per case
        total_pos_specs = extract.daily_test_logs[-1]['tot_pcr_pos']
        total_cases = extract.daily_case_logs[-1]['total_cases_repo']
        duplicate_specs = total_pos_specs - total_cases
        dupe_ratio = floor(1 / (duplicate_specs / total_pos_specs))
        print('duplicate_specs: {}'.format(duplicate_specs))
        print('dupe_ratio: {}'.format(dupe_ratio))

        # A simple FIFO queue
        testing_queue = queue.SimpleQueue()
        pos_specs_counted = 0
        skipped_dupes = 0

        # Loop through daily test logs
        for test_log in extract.daily_test_logs:
            timestamp = test_log['date']
            new_pos_tests_administered = test_log['daily_pos_spec']

            # Collect non-duplicate positive specs for this day
            for n in range(new_pos_tests_administered):
                pos_specs_counted += 1

                # Skip if a duplicate
                if skipped_dupes < duplicate_specs:
                    is_dupe = pos_specs_counted % dupe_ratio == 0
                    if is_dupe:
                        skipped_dupes += 1
                        continue

                virus_test = CovidVirusTest(spec_timestamp=timestamp, result='positive')
                testing_queue.put(virus_test)

        print('total_cases: {}'.format(total_cases))
        print('testing_queue size: {}'.format(testing_queue.qsize()))
        breakpoint()

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

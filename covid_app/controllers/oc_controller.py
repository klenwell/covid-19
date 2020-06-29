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

    # python app.py oc dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        url = "https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_testing_csv/FeatureServer/0/query?where=daily_test_repo+IS+NOT+NULL&objectIds=&time=&resultType=none&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=date&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="

        import requests
        from datetime import date, timedelta, datetime
        ts_to_date = lambda ts: datetime.utcfromtimestamp(ts/1000).date()

        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        features = json_data['features']
        data = [f['attributes'] for f in features if f.get('attributes')]

        tests = [(ts_to_date(d['date']), d['daily_test_repo']) for d in data]
        print(tests[-10:])

        breakpoint()

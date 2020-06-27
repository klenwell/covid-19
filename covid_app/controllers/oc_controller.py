from datetime import date
from cement import Controller
from cement import ex as expose

from covid_app.analytics.oc_by_day import OcByDayAnalysis


class OcController(Controller):
    class Meta:
        label = 'oc'
        stacked_on = 'base'
        stacked_type = 'nested'

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
        import requests
        url = "https://services2.arcgis.com/LORzk2hk9xzHouw9/ArcGIS/rest/services/occovid_main_csv/FeatureServer/0/query?where=0%3D0&objectIds=&time=&resultType=none&outFields=date%2Cdaily_tests%2Cdaily_cases%2Cdaily_dth%2Cdaily_hosp%2Cdaily_icu&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=date&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
        response = requests.get(url)
        response.raise_for_status()
        payload = response.json()
        data = [f['attributes'] for f in payload['features'] if f.get('attributes')]
        breakpoint()

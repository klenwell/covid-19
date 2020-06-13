from cement import Controller
from cement import ex as expose


from ..services.oc_health_service import OCHealthService
from ..services.mi_health_service import MiHealthService


class BaseController(Controller):
    class Meta:
        label = 'base'

    # python app.py oc-daily
    @expose(
        help="Export data from OC HCA site to csv file.",
        arguments=[
            (['-a'], dict(dest='archive', action='store',
                          help='Extract data from provided URL for archived web page.'))
        ]
    )
    def oc_daily(self):
        archive_url = self.app.pargs.archive

        if archive_url:
            csv = OCHealthService.export_archive(archive_url)
        else:
            csv = OCHealthService.export_daily_csv()

        vars = {'csv': csv}
        self.app.render(vars, 'oc_daily.jinja2')

    # python app.py kent-daily
    @expose(help="Export MI-6 data from NY Times repo to csv file.")
    def kent_daily(self):
        result = MiHealthService.export_daily_kent_csv()
        print(result)

    # python app.py interactive
    # This command can be used for testing and development.
    @expose(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        import requests, json
        from datetime import datetime
        url = "https://wabi-us-gov-iowa-api.analysis.usgovcloudapi.net/public/reports/querydata?synchronous=true"
        body = """{"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"t1","Entity":"Testing_Data"},{"Name":"c","Entity":"Cases by County"}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"t1"}},"Property":"TestType"},"Name":"Testing_Data.TestType"},{"Column":{"Expression":{"SourceRef":{"Source":"t1"}},"Property":"MessageDate"},"Name":"Testing_Data.MessageDate"},{"Aggregation":{"Expression":{"Column":{"Expression":{"SourceRef":{"Source":"t1"}},"Property":"TestCount"}},"Function":0},"Name":"CountNonNull(Testing_Data.TestCount)"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"c"}},"Property":"COUNTY"}}],"Values":[[{"Literal":{"Value":"'Kent'"}}]]}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[1,2]}]},"Secondary":{"Groupings":[{"Projections":[0]}]},"DataReduction":{"DataVolume":4,"Primary":{"Sample":{}},"Secondary":{"Top":{}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"3538771d-70f8-4399-9760-267975e37f65","Sources":[{"ReportId":"f489615d-c09e-43f9-b6bb-db2832eb0e0d"}]}}],"cancelQueries":[],"modelId":282246}"""

        headers = {
            'Host': 'wabi-us-gov-iowa-api.analysis.usgovcloudapi.net',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https',
            'ActivityId': '34d568b0-c29e-4f30-9cf0-f04afd959aca',
            'RequestId': '8ea32a6f-d19c-c4b7-79b2-641759d959df',
            'X-PowerBI-ResourceKey': '1ccb55ad-71e0-47fe-8762-bd11b89b00f5',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https',
            'DNT': '1',
            'Connection': 'keep-alive'
        }

        json_data = json.loads(body)

        res = requests.post(url, json=json_data, headers=headers)
        gov = res.json()
        gov_data = gov['results'][0]['result']['data']
        test_data = gov_data['dsr']['DS'][0]['PH'][0]['DM0'][1:]

        daily_tests = {}
        for td in test_data:
            ts = td['G0']
            date = datetime.utcfromtimestamp(ts/1000).date()
            viral_tests = td['X'][0]['M0']
            daily_tests[date] = viral_tests

        print(len(test_data))
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

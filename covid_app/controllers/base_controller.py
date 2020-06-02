from cement import Controller
from cement import ex as expose
import requests
import json


class BaseController(Controller):
    class Meta:
        label = 'base'

    # python app.py interactive
    @expose(help="Run the Application interactively.")
    def interactive(self):
        oc_site = "https://occovid19.ochealthinfo.com/coronavirus-in-oc"
        response = requests.get(oc_site)
        html = response.text
        _, tail = html.split('caseArr =')
        payload, _ = tail.split(';', 1)
        cases = json.loads(payload)
        breakpoint()

    # python app.py test -f foo arg1 extra2 extra2
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
        data = {'args': self.app.pargs}
        self.app.render(data, 'test.jinja2')

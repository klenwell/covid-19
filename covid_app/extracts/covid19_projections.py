import requests
import json
from datetime import datetime


EXTRACT_URL = 'https://covid19-projections.com/us-ca-orange'
DATE_F = '%Y-%m-%d'


class Covid19ProjectionsExtract:
    #
    # Static Methods
    #
    @staticmethod
    def oc_effective_reproduction():
        """Returns a dict: {date: count, ...} for Orange County, CA.
        """
        extract = Covid19ProjectionsExtract()
        html = extract.fetch_data_source()
        daily_rts_dict = extract.filter_oc_rts(html)
        return daily_rts_dict

    #
    # Instance Methods
    #
    def __init__(self):
        self.url = EXTRACT_URL

    def filter_oc_rts(self, html):
        """Returns a dict: {date: count, ...}
        """
        daily_values = {}

        # Extract json list from embedded js
        data_str = self.extract_json_data_from_embedded_js(html)

        # json string to list
        plot_data = json.loads(data_str)

        # Rt data is in last list.
        rt_data = plot_data[-1]

        # Map dates to Rt values
        for n in range(len(rt_data['x'])):
            date_str = rt_data['x'][n]
            rt = rt_data['y'][n]
            date = datetime.strptime(date_str, DATE_F).date()
            daily_values[date] = rt

        # Return as dict: {date: Rt}
        return daily_values

    #
    # Private
    #
    def fetch_data_source(self):
        response = requests.get(self.url)
        response.raise_for_status()  # will raise a requests.exceptions.HTTPError error
        return response.text

    def extract_json_data_from_embedded_js(self, html):
        _, tail = html.split('Plotly.newPlot', 1)
        _, tail = tail.split('[', 1)
        head, _ = tail.split("\n", 1)
        data, _ = head.rsplit(']', 1)

        # Lost containing bracket during parsing. Restores them.
        json_list = '[{}]'.format(data)

        return json_list

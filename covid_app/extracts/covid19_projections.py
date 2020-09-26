from datetime import datetime
from urllib.parse import urljoin
import requests
import json


BASE_URL = 'https://covid19-projections.com'
DATE_F = '%Y-%m-%d'


class Covid19ProjectionsExtract:
    #
    # Static Methods
    #
    @staticmethod
    def oc_effective_reproduction():
        """Returns a dict: {date: count, ...} for Orange County, CA.
        """
        url_path = 'us-ca-orange'
        url = urljoin(BASE_URL, url_path)
        extract = Covid19ProjectionsExtract(url)
        html = extract.fetch_data_source()
        daily_rts_dict = extract.filter_rts(html)
        return daily_rts_dict

    @staticmethod
    def us_effective_reproduction():
        """Returns a dict: {date: count, ...} for US.
        """
        url_path = 'us'
        url = urljoin(BASE_URL, url_path)
        extract = Covid19ProjectionsExtract(url)
        html = extract.fetch_data_source()
        daily_rts_dict = extract.filter_rts(html)
        return daily_rts_dict

    #
    # Instance Methods
    #
    def __init__(self, url):
        self.url = url

    def filter_rts(self, html):
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
        # Isolate the start of the embedded data string.
        _, tail = html.split('Plotly.newPlot', 1)
        _, tail = tail.split('[', 1)

        # Find a slice point for end of Rt data.
        end_marker = 'Deaths per day'
        head, _ = tail.split(end_marker, 1)

        # Now backtrack to end of the data list.
        data, _ = head.rsplit(']', 1)

        # Lost containing bracket during parsing. Restores them.
        json_list = '[{}]'.format(data)

        return json_list

    def broken_extract_json_data_from_embedded_js(self, html):
        _, tail = html.split('Plotly.newPlot', 1)
        _, tail = tail.split('[', 1)
        head, _ = tail.split("\n", 1)
        data, _ = head.rsplit(']', 1)

        # Lost containing bracket during parsing. Restores them.
        json_list = '[{}]'.format(data)

        return json_list

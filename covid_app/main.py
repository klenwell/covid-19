from cement import App
from .controllers.base_controller import BaseController
from .controllers.oc_controller import OcController
from .controllers.github_action_controller import GithubActionController


class CovidApp(App):
    class Meta:
        label = 'covid_app'

        # Use views directory for output templates
        # https://docs.builtoncement.com/extensions/jinja2#application-meta-options
        extensions = ['jinja2']
        output_handler = 'jinja2'
        template_dir = './covid_app/views'

        handlers = [BaseController, OcController, GithubActionController]

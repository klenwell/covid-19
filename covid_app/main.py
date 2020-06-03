from cement import App
from .controllers.base_controller import BaseController


class CovidApp(App):
    class Meta:
        label = 'bad_axe'

        # Use views directory for output templates
        # https://docs.builtoncement.com/extensions/jinja2#application-meta-options
        extensions = ['jinja2']
        output_handler = 'jinja2'
        template_dir = './covid_app/views'

        handlers = [BaseController]

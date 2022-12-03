from cement import Controller
from cement import ex as expose


class GithubActionController(Controller):
    class Meta:
        label = 'gha'
        stacked_on = 'base'
        stacked_type = 'nested'

    #
    # Other Commands
    #
    # python app.py gha hello
    @expose(help="Simple script that outputs hello.")
    def hello(self):
        print('Hello Github!')

    # python app.py gha dev
    @expose(help="For rapid testing and development.")
    def dev(self):
        print('Hello Github!')
        breakpoint()

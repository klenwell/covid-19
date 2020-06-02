"""
Klenwell COVID-19
klenwell@gmail.com

Main application entry point:

    $ python app.py
"""
from covid_app.main import CovidApp


if __name__ == "__main__":
    with CovidApp() as app:
        app.run()

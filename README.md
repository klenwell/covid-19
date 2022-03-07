# covid-19
This is a Python command-line application developed using [the Cement framework](https://docs.builtoncement.com/) as the missing CSV export feature for the OC Health Care Agency's [COVID-19 dashboard](https://occovid19.ochealthinfo.com/coronavirus-in-oc).

I use it to help maintain this COVID-19 spreadsheet:

- [OC C19 Data](https://docs.google.com/spreadsheets/d/e/2PACX-1vSxCDL6xIQll_G3zW737SwkjB_Y9i5stL6ccF4Z3jFCLgaLDcrWIfquzc99DnYk_QUQQuiQbsgsXiJQ/pubhtml)


## Installation
- Using [pyenv](https://github.com/pyenv/pyenv#installation), install Python version `3.8.x`. (`3.8.1` is the version I used):

      pyenv install 3.8.1

- Clone repository:

      git clone git@github.com:klenwell/covid-19.git

- Set Python version:

      cd covid-19
      pyenv local 3.8.1

- Install dependencies:

      pip install -r requirements.txt


## Usage
### Export Current Data
To export the latest Orange County COVID-19 data from the [OC Health Care Agency](https://occovid19.ochealthinfo.com/coronavirus-in-oc):

    python app.py oc daily-v2

When successful, it will generate a CSV files for case and immunity data and output something like this:

```
OC Daily COVID-19 Data Export v2
================================
## Data
CSV Path: /home/klenwell/projects/covid-19/data/oc/oc-hca.csv
Runtime: 0.8338844776153564 s

Start Date: 2020-01-22
End Date: 2022-03-04
Rows: 773

## Immunity
CSV Path: /home/klenwell/projects/covid-19/data/oc/oc-immunity.csv
Runtime: 1.5266637802124023 s

Infectious: 10758.0
Recovered:  859413.0733333332
Vaccinated: 1523281.7587037035

Start Date: 2020-01-22
End Date: 2022-03-04
Rows: 773
```


## Testing
There are a few tests. At this time, they are focused mainly on making quick fixes for breaking changes in page source formatting.

To run the full test suite:

    nosetests


## Development
The app comes packaged with [flake8](http://flake8.pycqa.org/en/latest/) for style guide enforcement. Before commiting any code, please run `flake8` and correct any reported issues:

```
# Bad: needs to be fixed
$ cd covid-19
$ flake8
./app.py:7:1: E302 expected 2 blank lines, found 1

# Good: no output
$ flake8
```

Please feel free to submit pull requests and file bugs on the issue tracker. This is a hobby project of mine so I cannot guarantee a prompt response.

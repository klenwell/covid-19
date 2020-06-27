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

    python app.py oc-daily

When successful, it will generate a CSV file and output something like this:

```
OC Daily COVID-19 Data Export

path: /home/klenwell/projects/covid-19/data/oc/oc-hca.csv
start: 2020-03-01
end: 2020-06-04
rows: 96
version: 2
```

**Note: Due to [changes in the OC HCA website and data sources](https://www.reddit.com/r/CoronavirusCA/comments/hgwb0t/where_can_you_and_i_find_countylevel_historical/), this extract is not currently able to import the latest data.**

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

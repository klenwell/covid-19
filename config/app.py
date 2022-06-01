from os.path import dirname, realpath, join as path_join

PROJECT_ROOT = dirname(dirname(realpath(__file__)))
APP_ROOT = path_join(PROJECT_ROOT, 'covid_app')

DATA_ROOT = path_join(PROJECT_ROOT, 'data')
GH_PAGES_ROOT = path_join(PROJECT_ROOT, 'docs')

# OC Wave Analysis
WAVE_ANALYSIS_CONFIG = {
    'window_size': 5,

    # Slope value distinguishing plateaus from rise/falls
    'flat_slope_threshold': 5,

    # This is the minimum size a phase needs to be (in days) not be flagged as micro
    # and merged.
    'min_phase_size': 14
}

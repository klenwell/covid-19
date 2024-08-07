"""
OC Immune Cohort

Estimates population immunity based on vaccines and recoveries for a given data.
"""
from datetime import datetime


#
# Constants
#
# These constants effective define the assumptions behind the vaccine efficacy model
# and how long it takes to fade.
PARTIAL_VAX_EFF = .75  # i.e. 75% effective
FULL_VAX_EFF = .9
RAMP_UP_WINDOW = 30  # days (to reach full efficacy)
FULL_EFF_WINDOW = 90  # days (before fade rate kicks in)
VAX_FADE_RATE = 1.0 / 270  # assume immunity fades to 0 over 9 months
INF_FADE_RATE = 1.0 / 180  # assume immunity fades to 0 over 6 months

# How long a reported positive case is assumed to be infectious.
INFECTION_WINDOW = 14  # days

# This is the factor by which positive cases are estimated to have been undercounted.
# Probably conservative. There are various studies that put the number between 4 and 7.
UNDERTEST_FACTOR = 3.0


class ImmuneCohort:
    #
    # Static Methods
    #
    @staticmethod
    def from_vax_record(record):
        admin_date = datetime.strptime(record['administered_date'], '%Y-%m-%d').date()
        partial_vax = int(record['partially_vaccinated'])
        full_vax = int(record['fully_vaccinated'])
        boost_vax = int(record['booster_recip_count'])
        infected = None
        return ImmuneCohort(admin_date, partial_vax, full_vax, boost_vax, infected)

    @staticmethod
    def count_active_infections(cohorts):
        counts = []
        recent_cohorts = reversed(cohorts)
        for cohort in recent_cohorts:
            counts.append(cohort.infections)
            if len(counts) >= INFECTION_WINDOW:
                break
        return sum(counts)

    #
    # Properties
    #
    @property
    def unfully_vaxxed_partials(self):
        return self.partial_vax_count - self.fully_vaxxed_partial_count

    @property
    def unboosted_full_vaxxed(self):
        return self.full_vax_count - self.boosted_full_vaxxed_count

    @property
    def infections(self):
        return self.infected_count * UNDERTEST_FACTOR

    #
    # Instance Method
    #
    def __init__(self, admin_date, partial_vax, full_vax, boost_vax, infected):
        self.date = admin_date
        self.partial_vax_count = partial_vax
        self.full_vax_count = full_vax
        self.boost_vax_count = boost_vax
        self.infected_count = infected

        # To track follow-up shots so they don't get double-counted
        self.fully_vaxxed_partial_count = 0
        self.boosted_full_vaxxed_count = 0

    def update_partially_vaxxed_cohorts(self, cohorts):
        """Restored from https://github.com/klenwell/covid-19/commit/2d0d29 for issue 55.

        Imagine case where someone gets shot 1 of 1/1 and shot 2 on 1/15. CDPH data will
        show a count for partial_vaxxed on 1/1 and fully_vaxed on 1/15 meaning person
        will be counted twice.

        To avoid overcount, this method will decrement 1/1 partial vaxxed count.
        """
        # Partials getting second (full) shot
        second_shots = self.full_vax_count
        for cohort in cohorts:
            surplus = cohort.update_partially_vaxxed(second_shots)
            if surplus <= 0:
                break

    def update_partially_vaxxed(self, second_shots):
        """Tracks vaxxed partials when they are estimated to later get a second shot.
        """
        if second_shots > self.unfully_vaxxed_partials:
            surplus = second_shots - self.unfully_vaxxed_partials
            self.fully_vaxxed_partial_count = self.partial_vax_count
            return surplus
        else:
            self.fully_vaxxed_partial_count += second_shots
            return 0

    def update_boosted_cohorts(self, cohorts):
        # Restored from https://github.com/klenwell/covid-19/commit/2d0d29
        surplus = self.boost_vax_count
        for cohort in cohorts:
            surplus = cohort.update_boosted(surplus)
            if surplus <= 0:
                break

        return self.boost_vax_count

    def update_boosted(self, booster_shots):
        """Tracks fully vaxxed when they are estimated to later get a booster.

        See how many booster shots we can apply for this date's cohort. Surplus will
        be returned and applied to next date.
        """
        # More booster than people eligible for this date. Apply and return surplus.
        if booster_shots > self.unboosted_full_vaxxed:
            surplus = booster_shots - self.unboosted_full_vaxxed
            self.boosted_full_vaxxed_count = self.full_vax_count
            return surplus
        # Not enough boosters. So apply them all and return 0.
        else:
            self.boosted_full_vaxxed_count += booster_shots
            return 0

    def compute_vax_immunity_for_date(self, report_date):
        days_out = (report_date - self.date).days
        partial = self.compute_partial_immunity(days_out)
        full = self.compute_full_immunity(days_out)
        booster = self.compute_booster_immunity(days_out)
        return partial + full + booster

    def compute_recovered_immunity_for_date(self, report_date):
        days_out = (report_date - self.date).days
        return self.compute_recovered_immunity(days_out)

    def compute_partial_immunity(self, days_out):
        # Ramp Up
        if days_out < RAMP_UP_WINDOW:
            vax_ramp_rate = PARTIAL_VAX_EFF / RAMP_UP_WINDOW
            vax_factor = vax_ramp_rate * days_out
        # Full Efficacy Window
        elif days_out >= RAMP_UP_WINDOW and days_out < FULL_EFF_WINDOW:
            vax_factor = PARTIAL_VAX_EFF
        # Ramp Down
        else:
            days_out -= FULL_EFF_WINDOW
            vax_factor = PARTIAL_VAX_EFF - (VAX_FADE_RATE * days_out)

        estimate = self.unfully_vaxxed_partials * vax_factor
        return max(estimate, 0)

    def compute_full_immunity(self, days_out):
        # Assumes this will be second shot and first shot was 4 weeks ago. Adjusts
        # days_out and efficacy windows accordingly.
        days_since_first_shot = 28
        adj_ramp_up_window = RAMP_UP_WINDOW + days_since_first_shot
        adj_full_eff_window = FULL_EFF_WINDOW + days_since_first_shot
        days_out += days_since_first_shot

        # Ramp Up
        if days_out < adj_ramp_up_window:
            vax_ramp_rate = FULL_VAX_EFF / RAMP_UP_WINDOW
            vax_factor = vax_ramp_rate * days_out
        # Full Efficacy Window
        elif days_out >= adj_ramp_up_window and days_out < adj_full_eff_window:
            vax_factor = FULL_VAX_EFF
        # Ramp Down
        else:
            days_out -= adj_full_eff_window
            vax_factor = FULL_VAX_EFF - (VAX_FADE_RATE * days_out)

        estimate = self.unboosted_full_vaxxed * vax_factor
        return max(estimate, 0)

    def compute_booster_immunity(self, days_out):
        # Ramp Up
        if days_out < RAMP_UP_WINDOW:
            vax_ramp_rate = FULL_VAX_EFF / RAMP_UP_WINDOW
            vax_factor = vax_ramp_rate * days_out
        # Full Efficacy Window
        elif days_out >= RAMP_UP_WINDOW and days_out < FULL_EFF_WINDOW:
            vax_factor = FULL_VAX_EFF
        # Ramp Down
        else:
            days_out -= FULL_EFF_WINDOW
            vax_factor = FULL_VAX_EFF - (VAX_FADE_RATE * days_out)

        estimate = self.boost_vax_count * vax_factor
        return max(estimate, 0)

    def compute_recovered_immunity(self, days_out):
        if days_out < INFECTION_WINDOW:
            return 0

        # Ramp Up
        if days_out < RAMP_UP_WINDOW:
            vax_ramp_rate = FULL_VAX_EFF / RAMP_UP_WINDOW
            vax_factor = vax_ramp_rate * days_out
        # Full Efficacy Window
        elif days_out >= RAMP_UP_WINDOW and days_out < FULL_EFF_WINDOW:
            vax_factor = FULL_VAX_EFF
        # Ramp Down
        else:
            days_out -= FULL_EFF_WINDOW
            vax_factor = FULL_VAX_EFF - (INF_FADE_RATE * days_out)

        estimate = self.infections * vax_factor
        return max(estimate, 0)

    def __repr__(self):
        f = '<ImmuneCohort date={} partial={} full={} boosted={} infected={}>'
        return f.format(self.date, self.partial_vax_count, self.full_vax_count,
                        self.boost_vax_count, self.infected_count)

"""
OC Immune Cohort

Estimates population immunity based on vaccines and recoveries for a given data.
"""


#
# Constants
#
PARTIAL_VAX_EFF = .75
FULL_VAX_EFF = .9
VAX_FADE_RATE = 1.0 / 270  # assume immunity fades to 0 over 9 months
INF_FADE_RATE = 1.0 / 180  # assume immunity fades to 0 over 9 months


class ImmuneCohort:
    #
    # Instance Method
    #
    def __init__(self, admin_date, partial_vax, full_vax, boost_vax, infected):
        self.date = admin_date
        self.partial_vax_count = partial_vax
        self.full_vax_count = full_vax
        self.boost_vax_count = boost_vax
        self.infected_count = infected

    def adjust_partial(self, full_vaxxed):
        """Subtracts partial when they are estimated to later get a second shot.
        """
        if full_vaxxed > self.partial_vax_count:
            adjusted = self.partial_vax_count
            self.partial_vax_count = 0
            return adjusted
        else:
            self.partial_vax_count -= full_vaxxed
            return full_vaxxed

    def adjust_boosted(self, boosted_count):
        """Subtracts full when they are estimated to later get a booster.
        """
        if boosted_count > self.full_vax_count:
            adjusted = self.full_vax_count
            self.full_vax_count = 0
            return adjusted
        else:
            self.full_vax_count -= boosted_count
            return boosted_count

    def compute_immunity_for_date(self, report_date):
        days_out = (report_date - self.date).days
        partial = self.compute_partial_immunity(days_out)
        full = self.compute_full_immunity(days_out)
        booster = self.compute_booster_immunity(days_out)
        recovered = self.compute_recovered_immunity(days_out)
        return partial + full + booster + recovered

    def compute_partial_immunity(self, vax_count, days_out):
        vax_factor = PARTIAL_VAX_EFF - (VAX_FADE_RATE * days_out)
        estimate = self.partial_vax_count * vax_factor
        return max(estimate, 0)

    def compute_full_immunity(self, days_out):
        vax_factor = FULL_VAX_EFF - (VAX_FADE_RATE * days_out)
        estimate = self.full_vax_count * vax_factor
        return max(estimate, 0)

    def compute_booster_immunity(self, days_out):
        vax_factor = FULL_VAX_EFF - (VAX_FADE_RATE * days_out)
        estimate = self.boost_vax_count * vax_factor
        return max(estimate, 0)

    def compute_recovered_immunity(self, days_out):
        if days_out < 14:
            return 0

        vax_factor = PARTIAL_VAX_EFF - (INF_FADE_RATE * days_out)
        estimate = self.infected_count * vax_factor
        return max(estimate, 0)

    def __repr__(self):
        f = '<ImmuneCohort date={} partial={} full={} boosted={} infected={}>'
        return f.format(self.date, self.partial_vax_count, self.full_vax_count,
                        self.boost_vax_count, self.infected_count)

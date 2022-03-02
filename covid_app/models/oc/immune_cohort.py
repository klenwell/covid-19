"""
OC Immune Cohort

Estimates population immunity based on vaccines and recoveries for a given data.
"""
from datetime import datetime


#
# Constants
#
PARTIAL_VAX_EFF = .75
FULL_VAX_EFF = .9
VAX_FADE_RATE = 1.0 / 270  # assume immunity fades to 0 over 9 months
INF_FADE_RATE = 1.0 / 180  # assume immunity fades to 0 over 9 months


class ImmuneCohort:
    @staticmethod
    def from_vax_record(record):
        admin_date = datetime.strptime(record['administered_date'], '%Y-%m-%d').date()
        partial_vax = int(record['partially_vaccinated'])
        full_vax = int(record['fully_vaccinated'])
        boost_vax = int(record['booster_recip_count'])
        infected = None
        return ImmuneCohort(admin_date, partial_vax, full_vax, boost_vax, infected)

    @property
    def unfully_vaxxed_partials(self):
        return self.partial_vax_count - self.fully_vaxxed_partial_count

    @property
    def unboosted_full_vaxxed(self):
        return self.full_vax_count - self.boosted_full_vaxxed_count

    #
    # Instance Method
    #
    def __init__(self, admin_date, partial_vax, full_vax, boost_vax, infected):
        self.date = admin_date
        self.partial_vax_count = partial_vax
        self.full_vax_count = full_vax
        self.boost_vax_count = boost_vax
        self.infected_count = infected

        # To track follow-up vaccinations
        self.fully_vaxxed_partial_count = 0
        self.boosted_full_vaxxed_count = 0

    def update_partial_vaxxed(self, full_vaxxed):
        """Tracks vaxxed partials when they are estimated to later get a second shot.
        """
        if full_vaxxed > self.unfully_vaxxed_partials:
            surplus = full_vaxxed - self.unfully_vaxxed_partials
            self.fully_vaxxed_partial_count = self.partial_vax_count
            return surplus
        else:
            self.fully_vaxxed_partial_count += full_vaxxed
            return 0

    def update_boosted(self, boosted_count):
        """Tracks fully vaxxed when they are estimated to later get a booster.
        """
        if boosted_count > self.unboosted_full_vaxxed:
            surplus = boosted_count - self.unboosted_full_vaxxed
            self.boosted_full_vaxxed_count = self.full_vax_count
            return surplus
        else:
            self.boosted_full_vaxxed_count += boosted_count
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

    def compute_immunity_for_date(self, report_date):
        vax_immunity = self.compute_vax_immunity_for_date(report_date)
        recovered = self.compute_recovered_immunity_for_date(report_date)
        return vax_immunity + recovered

    def compute_partial_immunity(self, days_out):
        vax_factor = PARTIAL_VAX_EFF - (VAX_FADE_RATE * days_out)
        estimate = self.unfully_vaxxed_partials * vax_factor
        return max(estimate, 0)

    def compute_full_immunity(self, days_out):
        vax_factor = FULL_VAX_EFF - (VAX_FADE_RATE * days_out)
        estimate = self.unboosted_full_vaxxed * vax_factor
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

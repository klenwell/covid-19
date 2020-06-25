from cement import Controller
from cement import ex as expose


class OcController(Controller):
    class Meta:
        label = 'oc'
        stacked_on = 'base'
        stacked_type = 'nested'

    # python app.py oc analyze-by-day
    @expose(help="Generate analysis of OC HCA data by day-of-week.")
    def analyze_by_day(self):
        from covid_app.models.oc_daily_log import OcDailyLog
        from datetime import date
        start_on = date(2020, 4, 26)
        end_on = date(2020, 6, 20)

        logs = OcDailyLog.all()
        logs_by_day = {}
        cases_by_day = {}

        for log in logs:
            if log.created_on < start_on or log.created_on > end_on:
                continue

            day_group = logs_by_day.get(log.day_of_week, [])
            day_group.append(log)
            logs_by_day[log.day_of_week] = day_group

        for day in logs_by_day.keys():
            cases_by_day[day] = sum([log.cases for log in logs_by_day[day]])

        print(cases_by_day)
        breakpoint()

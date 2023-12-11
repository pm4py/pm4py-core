from pm4py.util.business_hours import BusinessHours
from pm4py.util.dt_parsing.variants import strpfromiso
import datetime
from workalendar.europe import Italy
from pm4py.util import constants


def execute_script():
    ts1 = 100000000
    ts2 = 110000000
    d1 = strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(ts1))
    d2 = strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(ts2))
    print(ts2-ts1)
    # default business hours: all the days of the week except Saturday and Sunday are working days.
    bh1 = BusinessHours(d1, d2, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS)
    print(bh1.get_seconds())
    # let's calculate the business hours using a proper work calendar.
    bh2 = BusinessHours(d1, d2, business_hour_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS, workcalendar=Italy())
    print(bh2.get_seconds())


if __name__ == "__main__":
    execute_script()

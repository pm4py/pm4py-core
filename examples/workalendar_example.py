from pm4py.util.business_hours import BusinessHours
import datetime
from workalendar.europe import Italy


def execute_script():
    ts1 = 100000000
    ts2 = 110000000
    d1 = datetime.datetime.fromtimestamp(ts1)
    d2 = datetime.datetime.fromtimestamp(ts2)
    print(ts2-ts1)
    # default business hours: all the days of the week except Saturday and Sunday are working days.
    bh1 = BusinessHours(d1, d2, worktiming=[[7, 12.5], [13, 17]])
    print(bh1.getseconds())
    # let's calculate the business hours using a proper work calendar.
    bh2 = BusinessHours(d1, d2, worktiming=[[7, 12.25], [13.25, 17]], workcalendar=Italy())
    print(bh2.getseconds())


if __name__ == "__main__":
    execute_script()

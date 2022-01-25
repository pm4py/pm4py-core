'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import datetime
from typing import List
from copy import copy
from pm4py.util import constants


def soj_time_business_hours_diff(st: datetime.datetime, et: datetime.datetime, worktiming: List[int],
                                 weekends: List[int],
                                 workcalendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR) -> float:
    """
    Calculates the difference between the provided timestamps based on the business hours

    Parameters
    -----------------
    st
        Start timestamp
    et
        Complete timestamp
    worktiming
        work schedule of the company (provided as a list where the first number is the start
            of the work time, and the second number is the end of the work time), if business hours are enabled
                                        Default: [7, 17] (work shift from 07:00 to 17:00)
    weekends
        indexes of the days of the week that are weekend
                                            Default: [6, 7] (weekends are Saturday and Sunday)

    Returns
    -----------------
    diff
        Difference in business hours
    """
    bh = BusinessHours(st.replace(tzinfo=None), et.replace(tzinfo=None),
                       worktiming=worktiming,
                       weekends=weekends, workcalendar=workcalendar)
    return bh.getseconds()


class BusinessHours:

    def __init__(self, datetime1, datetime2, **kwargs):
        self.datetime1 = datetime1
        self.datetime2 = datetime2
        self.weekends = kwargs["weekends"] if "weekends" in kwargs else [6, 7]
        # supports either specification of uninterrupted work timing,
        # or with breaks
        self.worktiming = kwargs["worktiming"] if "worktiming" in kwargs else [7, 17]
        # workalendar calendar (it permits to query if a given day
        # is a working day in a given culture)
        self.workcalendar = kwargs[
            "workcalendar"] if "workcalendar" in kwargs else constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR

        if type(self.worktiming[0]) is int or type(self.worktiming[0]) is float:
            self.worktiming = [self.worktiming]

        if type(self.worktiming) is not dict:
            self.worktiming = {i: self.worktiming for i in range(0, 7)}

    def getseconds(self):
        current_date = copy(self.datetime1)

        summ = 0

        for dayweek in self.worktiming:
            for wt in self.worktiming[dayweek]:
                timedelta_nd = datetime.timedelta(days=1.0)

                dt1 = datetime.datetime(year=current_date.year, month=current_date.month, day=current_date.day,
                                        hour=int(wt[0]), minute=int((wt[0] - int(wt[0])) * 60))
                dt2 = datetime.datetime(year=current_date.year, month=current_date.month, day=current_date.day,
                                        hour=int(wt[1]), minute=int((wt[1] - int(wt[1])) * 60))

                while dt1 <= self.datetime2:
                    if dt2 > self.datetime2:
                        dt2 = self.datetime2

                    if dt1.weekday() == dayweek:
                        timedelta_nd = datetime.timedelta(days=7.0)
                        if self.__is_working_day(dt1):
                                diff = dt2.timestamp() - max(dt1, self.datetime1).timestamp()
                                if diff > 0:
                                    summ += diff

                    dt1 = dt1 + timedelta_nd
                    dt2 = dt2 + timedelta_nd

        return summ

    def __is_working_day(self, dt):
        if self.workcalendar is None:
            return dt.isoweekday() not in self.weekends
        return self.workcalendar.is_working_day(dt)

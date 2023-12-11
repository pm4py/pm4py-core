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
import math
from datetime import timedelta, datetime, time
from typing import List, Tuple

from pm4py.util import constants
from pm4py.util.dt_parsing.variants import strpfromiso


def soj_time_business_hours_diff(st: datetime, et: datetime, business_hour_slots: List[Tuple[int]],
                                 work_calendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR) -> float:
    """
    Calculates the difference between the provided timestamps based on the business hours

    Parameters
    -----------------
    st
        Start timestamp
    et
        Complete timestamp
    business_hour_slots
        work schedule of the company, provided as a list of tuples where each tuple represents one time slot of business
        hours. One slot i.e. one tuple consists of one start and one end time given in seconds since week start, e.g.
        [
            (7 * 60 * 60, 17 * 60 * 60),
            ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60),
            ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),
        ]
        meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00
    work_calendar
        work calendar (it permits querying if a given day is a working day in a given culture)

    Returns
    -----------------
    diff
        Difference in business hours
    """
    bh = BusinessHours(st, et,
                       business_hour_slots=business_hour_slots, work_calendar=work_calendar)
    return bh.get_seconds()


def get_overlapping_time(timespan1_begin: datetime, timespan1_end: datetime,
                         timespan2_begin: datetime, timespan2_end: datetime) -> float:
    latest_start = max(timespan1_begin, timespan2_begin)
    earliest_end = min(timespan1_end, timespan2_end)
    delta = (earliest_end - latest_start).total_seconds()
    overlap = max(0.0, delta)
    return overlap


class BusinessHours:
    def __init__(self, datetime1, datetime2, **kwargs):
        self.datetime1 = datetime1.replace(tzinfo=None)
        self.datetime2 = datetime2.replace(tzinfo=None)

        self.business_hour_slots = kwargs[
            "business_hour_slots"] if "business_hour_slots" in kwargs else constants.DEFAULT_BUSINESS_HOUR_SLOTS

        # union of business hour slots in order to avoid overlapping business hours
        self.business_hour_slots_unified = []
        for begin, end in sorted(self.business_hour_slots):
            if self.business_hour_slots_unified and self.business_hour_slots_unified[-1][1] >= begin - 1:
                self.business_hour_slots_unified[-1][1] = max(self.business_hour_slots_unified[-1][1], end)
            else:
                self.business_hour_slots_unified.append([begin, end])

        # work calendar (it permits querying if a given day is a working day in a given culture) - not used yet
        self.work_calendar = kwargs[
            "work_calendar"] if "work_calendar" in kwargs else constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR

    def get_seconds(self):
        sum = 0
        week_start = self.datetime1.date() - timedelta(days=self.datetime1.weekday())

        for bhs, bhe in self.business_hour_slots_unified:
            begin_day_of_week = math.floor(bhs / 60 / 60 / 24)
            begin_seconds_of_day = bhs - 24 * 60 * 60 * begin_day_of_week
            bh_start = datetime.combine(week_start, time.min) + timedelta(days=begin_day_of_week) + timedelta(
                seconds=begin_seconds_of_day)

            end_day_of_week = math.floor(bhe / 60 / 60 / 24)
            end_seconds_of_day = bhe - 24 * 60 * 60 * end_day_of_week
            bh_end = datetime.combine(week_start, time.min) + timedelta(days=end_day_of_week) + timedelta(
                seconds=end_seconds_of_day)

            overlapping_time = get_overlapping_time(self.datetime1, self.datetime2, bh_start, bh_end)
            sum += overlapping_time

            while True:
                bh_start += timedelta(days=7)
                bh_end += timedelta(days=7)

                overlapping_time = get_overlapping_time(self.datetime1, self.datetime2, bh_start, bh_end)

                if overlapping_time <= 0:
                    break

                sum += overlapping_time

        return sum

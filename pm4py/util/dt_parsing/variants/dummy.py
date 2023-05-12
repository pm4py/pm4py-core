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


def apply(dt):
    if dt.endswith("Z"):
        # Z at the end of date means UTC, but that is not ISO format.
        # Replace "Z" with "+00:00" that is also UTC
        dt = dt[:-1] + "+00:00"
    dt0 = dt.split("T")
    datepart = dt0[0].split("-")
    dt2 = dt0[1].split("+")
    hourpart = dt2[0].split(":")
    year = int(datepart[0])
    month = int(datepart[1])
    day = int(datepart[2])
    hour = int(hourpart[0])
    minute = int(hourpart[1])
    sms = hourpart[2].split(".")
    second = int(sms[0])
    if len(sms) > 1:
        microseconds = int(sms[1])*1000
    else:
        microseconds = 0

    return datetime.datetime(year, month, day, hour, minute, second, microseconds)

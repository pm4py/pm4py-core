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
def derive_end_activities_from_log(log, activity_key):
    """
    Derive end activities from log

    Parameters
    -----------
    log
        Log object
    activity_key
        Activity key

    Returns
    -----------
    e
        End activities
    """
    e = set()
    for t in log:
        if len(t) > 0:
            if activity_key in t[len(t) - 1]:
                e.add(t[len(t) - 1][activity_key])
    return e


def derive_start_activities_from_log(log, activity_key):
    """
    Derive start activities from log

    Parameters
    -----------
    log
        Log object
    activity_key
        Activity key

    Returns
    -----------
    s
        Start activities
    """
    s = set()
    for t in log:
        if len(t) > 0:
            if activity_key in t[0]:
                s.add(t[0][activity_key])
    return s

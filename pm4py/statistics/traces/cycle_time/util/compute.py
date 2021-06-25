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
from typing import List, Tuple


def cycle_time(events: List[Tuple[float, float]], num_instances: int) -> float:
    """
    Computes the cycle time given a list of events (having a start and a complete timestamp)
    and the number of instances of the log

    The definition that has been followed is the one proposed in:
    https://www.presentationeze.com/presentations/lean-manufacturing-just-in-time/lean-manufacturing-just-in-time-full-details/process-cycle-time-analysis/calculate-cycle-time/#:~:text=Cycle%20time%20%3D%20Average%20time%20between,is%2024%20minutes%20on%20average.

    So:
    Cycle time  = Average time between completion of units.

    Example taken from the website:
    Consider a manufacturing facility, which is producing 100 units of product per 40 hour week.
    The average throughput rate is 1 unit per 0.4 hours, which is one unit every 24 minutes.
    Therefore the cycle time is 24 minutes on average.

    Parameters
    ---------------
    events
        List of events (each event is a tuple having the start and the complete timestamp)
    num_instances
        Number of instances of the log

    Returns
    ---------------
    cycle_time
        Cycle time
    """
    events = sorted(events, key=lambda x: (x[0], x[1]))

    st = events[0][0]
    et = events[0][1]

    production_time = 0

    for i in range(1, len(events)):
        this_st = events[i][0]
        this_et = events[i][1]

        if this_st > et:
            production_time += (et - st)
            st = this_st

        et = max(et, this_et)

    return production_time / num_instances

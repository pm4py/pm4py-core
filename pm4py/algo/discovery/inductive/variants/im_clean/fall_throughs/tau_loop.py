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
from typing import Optional

from pm4py.objects.log.obj import EventLog, Trace


def detect(log: EventLog, start_activities, act_key: str) -> Optional[EventLog]:
    proj = EventLog()
    for t in log:
        x = 0
        for i in range(1, len(t)):
            if t[i][act_key] in start_activities:
                proj.append(Trace(t[x:i]))
                x = i
        proj.append(Trace(t[x:len(t)]))
    return proj if len(proj) > len(log) else None

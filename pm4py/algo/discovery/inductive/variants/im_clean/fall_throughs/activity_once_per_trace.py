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
from typing import Dict, Optional, List

import pm4py
from pm4py.objects.log.obj import EventLog


def detect(log: EventLog, alphabet: Dict[str, int], act_key: str) -> Optional[str]:
    candidates = set(alphabet.keys())
    for t in log:
        tr = list(map(lambda e: e[act_key], t))
        cc = [x for x in candidates]
        for candi in cc:
            if len(list(filter(lambda e: e == candi, tr))) != 1:
                candidates.remove(candi)
        if len(candidates) == 0:
            return None
    return next(iter(candidates))


def project(log: EventLog, activity: str, activity_key: str) -> List[EventLog]:
    proj = EventLog()
    for t in log:
        proj.append(pm4py.filter_trace(lambda e: e[activity_key] != activity, t))
    return [proj]

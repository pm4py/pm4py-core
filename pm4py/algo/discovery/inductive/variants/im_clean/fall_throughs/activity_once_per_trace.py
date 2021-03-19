from typing import Dict, Optional, List

import pm4py
from pm4py.objects.log.log import EventLog


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

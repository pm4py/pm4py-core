from typing import Dict, Optional, List, Collection
import copy

import pm4py
from pm4py.objects.log.obj import EventLog



def detect(log: List[List[int]], alphabet: Collection[int]) -> Optional[str]:
    candidates = copy.copy(alphabet)
    for t in log:
        tr = list(map(lambda e: e, t))
        cc = [x for x in candidates]
        for candi in cc:
            if len(list(filter(lambda e: e == candi, tr))) != 1:
                candidates.remove(candi)
        if len(candidates) == 0:
            return None
    return next(iter(candidates))


def project(log: List[List[int]], activity: int) -> List[EventLog]:
    return [[list(filter(lambda e: e != activity, t)) for t in log]]

from collections import Counter
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class StrictTauLoop(FallThrough[UVCL]):

    @classmethod
    def _get_projected_log(cls, log: UVCL) -> UVCL:
        start_activities = comut.get_start_activities(log)
        end_activities = comut.get_end_activities(log)
        proj = Counter()
        for t in log:
            x = 0
            for i in range(1, len(t)):
                if t[i] in start_activities and t[i - 1] in end_activities:
                    proj.update({t[x:i]: log[t]})
                    x = i
            proj.update({t[x:len(t)]: log[t]})
        return proj

    @classmethod
    def holds(cls, log: UVCL) -> bool:
        return sum(cls._get_projected_log(log).values()) > sum(log.values())

    @classmethod
    def apply(cls, log: UVCL) -> Optional[Tuple[ProcessTree, List[UVCL]]]:
        proj = cls._get_projected_log(log)
        if sum(proj.values()) > sum(log.values()):
            return ProcessTree(operator=Operator.LOOP), [proj, []]

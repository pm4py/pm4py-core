from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough, T
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UCL


class StrictTauLoop(FallThrough[UCL]):

    @classmethod
    def _get_projected_log(cls, log: UCL):
        start_activities = comut.get_start_activities(log)
        end_activities = comut.get_end_activities(log)
        proj = []
        for t in log:
            x = 0
            for i in range(1, len(t)):
                if t[i] in start_activities and t[i - 1] in end_activities:
                    proj.append(t[x:i])
                    x = i
            proj.append(t[x:len(t)])
        return proj

    @classmethod
    def holds(cls, log: UCL) -> bool:
        return len(cls._get_projected_log(log)) > len(log)

    @classmethod
    def apply(cls, log: UCL) -> Optional[Tuple[ProcessTree, List[UCL]]]:
        proj = cls._get_projected_log(log)
        if len(cls._get_projected_log(log)) > len(log):
            return ProcessTree(operator=Operator.LOOP), [proj, []]

from collections import Counter
from multiprocessing import Pool, Manager
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class StrictTauLoopUVCL(FallThrough[IMDataStructureUVCL]):

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
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        log = obj.data_structure
        return sum(cls._get_projected_log(log).values()) > sum(log.values())

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        log = obj.data_structure
        proj = cls._get_projected_log(log)
        if sum(proj.values()) > sum(log.values()):
            return ProcessTree(operator=Operator.LOOP), [IMDataStructureUVCL(proj), IMDataStructureUVCL(Counter())]

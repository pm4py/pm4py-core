from collections import Counter
from typing import Optional, Tuple, List, Any, Dict

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.activity_once_per_trace import ActivityOncePerTraceUVCL
from pm4py.algo.discovery.powl.inductive.fall_through.activity_concurrent import POWLActivityConcurrentUVCL
from pm4py.objects.powl.obj import StrictPartialOrder
from pm4py.objects.process_tree.obj import ProcessTree, Operator


class POWLActivityOncePerTraceUVCL(ActivityOncePerTraceUVCL, POWLActivityConcurrentUVCL):
    @classmethod
    def apply(cls, obj: IMDataStructureUVCL,
              pool=None,
              manager=None,
              parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[StrictPartialOrder, List[IMDataStructureUVCL]]]:

        candidate = cls._get_candidate(obj, pool, manager, parameters)
        if candidate is None:
            return None
        log = obj.data_structure
        l_a = Counter()
        l_other = Counter()
        for t in log:
            l_a.update({tuple(filter(lambda e: e == candidate, t)): log[t]})
            l_other.update({tuple(filter(lambda e: e != candidate, t)): log[t]})
        children = [IMDataStructureUVCL(l_a), IMDataStructureUVCL(l_other)]
        return StrictPartialOrder(children), children

from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough, T
from pm4py.algo.discovery.inductive.variants.im import IM
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UCL


class ActivityConcurrent(FallThrough[UCL]):

    @classmethod
    def _get_candidates(cls, log: UCL):
        candidates = comut.get_alphabet(log)
        cc = set()
        for a in candidates:
            l_alt = [list(filter(lambda e: e != a, t)) for t in log]
            cut = IM().find_cut(l_alt)
            if cut is not None:
                cc.add(a)
                break
        return cc

    @classmethod
    def holds(cls, log: UCL) -> bool:
        return len(cls._get_candidates(log)) > 0

    @classmethod
    def apply(cls, log: UCL) -> Optional[Tuple[ProcessTree, List[UCL]]]:
        candidates = cls._get_candidates(log)
        if len(candidates) > 0:
            a = next(iter(candidates))
            return ProcessTree(operator=Operator.PARALLEL), [[list(filter(lambda e: e == a, t)) for t in log],
                                                             [list(filter(lambda e: e != a, t)) for t in log]]
        else:
            return None

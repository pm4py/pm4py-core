import copy
from typing import Optional, Tuple, List, Collection, Any

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UCL


class ActivityOncePerCase(FallThrough[UCL]):

    @classmethod
    def _get_candidates(cls, log) -> Collection[Any]:
        candidates = copy.copy(comut.get_alphabet(log))
        for t in log:
            cc = [x for x in candidates]
            for candi in cc:
                if len(list(filter(lambda e: e == candi, t))) != 1:
                    candidates.remove(candi)
            if len(candidates) == 0:
                return candidates
        return candidates

    @classmethod
    def holds(cls, log: UCL) -> bool:
        return len(cls._get_candidates(log)) > 0

    @classmethod
    def apply(cls, log: UCL) -> Optional[Tuple[ProcessTree, List[UCL]]]:
        candidates = cls._get_candidates()
        if len(candidates) > 0:
            a = next(iter(candidates))
            return ProcessTree(operator=Operator.PARALLEL), [[[a]], [list(filter(lambda e: e != a, t)) for t in log]]
        else:
            return None

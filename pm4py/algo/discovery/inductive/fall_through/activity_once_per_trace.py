import copy
from collections import Counter
from typing import Optional, Tuple, List, Collection, Any

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class ActivityOncePerCase(FallThrough[UVCL]):

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
    def holds(cls, log: UVCL) -> bool:
        return len(cls._get_candidates(log)) > 0

    @classmethod
    def apply(cls, log: UVCL) -> Optional[Tuple[ProcessTree, List[UVCL]]]:
        candidates = cls._get_candidates(log)
        if len(candidates) > 0:
            a = next(iter(candidates))
            l_a = Counter()
            l_other = Counter()
            for t in log:
                l_a[tuple(filter(lambda e: e == a, t))] = log[t]
                l_other[tuple(filter(lambda e: e != a, t))] = log[t]
            return ProcessTree(operator=Operator.PARALLEL), [l_a, l_other]
        else:
            return None

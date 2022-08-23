from collections import Counter
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class ActivityConcurrentUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def _get_candidates(cls, log: UVCL):
        candidates = comut.get_alphabet(log)
        cc = set()
        for a in candidates:
            l_alt = Counter()
            for t in log:
                l_alt[tuple(filter(lambda e: e != a, t))] = log[t]
            cut = cls._find_cut(l_alt)
            if cut is not None:
                cc.add(a)
                break
        return cc

    @classmethod
    def _find_cut(cls, log: IMDataStructureUVCL) -> Optional[Tuple[ProcessTree, List[UVCL]]]:
        for c in CutFactory.get_cuts(log, IMInstance.IM):
            r = c.apply(log)
            if r is not None:
                return r
        return None

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        return len(cls._get_candidates(obj.data_structure)) > 0

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        candidates = cls._get_candidates(obj.data_structure)
        log = obj.data_structure
        if len(candidates) > 0:
            a = next(iter(candidates))
            l_a = Counter()
            l_other = Counter()
            for t in log:
                l_a[tuple(filter(lambda e: e == a, t))] = log[t]
                l_other[tuple(filter(lambda e: e != a, t))] = log[t]
            return ProcessTree(operator=Operator.PARALLEL), [IMDataStructureUVCL(l_a), IMDataStructureUVCL(l_other)]
        else:
            return None

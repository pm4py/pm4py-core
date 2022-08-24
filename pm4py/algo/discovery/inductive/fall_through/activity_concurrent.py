from collections import Counter
from typing import Optional, Tuple, List, Collection, Any

from pm4py.algo.discovery.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut


class ActivityConcurrentUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def _get_candidates(cls, obj: IMDataStructureUVCL) -> Collection[Any]:
        log = obj.data_structure
        candidates = comut.get_alphabet(log)
        cc = set()
        if len(candidates) > 2:
            for a in candidates:
                l_alt = Counter()
                for t in log:
                    l_alt[tuple(filter(lambda e: e != a, t))] = log[t]
                cut = cls._find_cut(IMDataStructureUVCL(l_alt))
                if cut is not None:
                    cc.add(a)
                    break
        return cc

    @classmethod
    def _find_cut(cls, obj: IMDataStructureUVCL) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        for c in CutFactory.get_cuts(obj, IMInstance.IM):
            r = c.apply(obj)
            if r is not None:
                return r
        return None

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        return len(cls._get_candidates(obj)) > 0

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        candidates = cls._get_candidates(obj)
        if len(candidates) > 0:
            log = obj.data_structure
            a = next(iter(candidates))
            l_a = Counter()
            l_other = Counter()
            for t in log:
                l_a.update({tuple(filter(lambda e: e == a, t)): log[t]})
                l_other.update({tuple(filter(lambda e: e != a, t)): log[t]})
            return ProcessTree(operator=Operator.PARALLEL), [IMDataStructureUVCL(l_a), IMDataStructureUVCL(l_other)]
        else:
            return None

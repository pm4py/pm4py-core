from typing import List, Optional, Tuple, TypeVar

from pm4py.algo.discovery.inductive.cuts.abc import Cut
from pm4py.algo.discovery.inductive.cuts.concurrency import ConcurrencyCutUVCL, ConcurrencyCutDFG
from pm4py.algo.discovery.inductive.cuts.loop import LoopCutUVCL, LoopCutDFG
from pm4py.algo.discovery.inductive.cuts.sequence import StrictSequenceCutUVCL, StrictSequenceCutDFG
from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceCutUVCL, ExclusiveChoiceCutDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=Cut)


class CutFactory:

    @classmethod
    def get_cuts(cls, obj: T, inst: IMInstance) -> List[S]:
        if inst is IMInstance.IM:
            if type(obj) is IMDataStructureUVCL:
                return [ExclusiveChoiceCutUVCL, StrictSequenceCutUVCL, ConcurrencyCutUVCL, LoopCutUVCL]
        if inst is IMInstance.IMd:
            if type(obj) is IMDataStructureDFG:
                return [ExclusiveChoiceCutDFG, StrictSequenceCutDFG, ConcurrencyCutDFG, LoopCutDFG]
        return list()

    @classmethod
    def find_cut(cls, obj: IMDataStructure, inst: IMInstance) -> Optional[Tuple[ProcessTree, List[T]]]:
        for c in CutFactory.get_cuts(obj, inst):
            r = c.apply(obj)
            if r is not None:
                return r
        return None
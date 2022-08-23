from typing import List

from pm4py.algo.discovery.inductive.cuts.abc import Cut
from pm4py.algo.discovery.inductive.cuts.concurrency import ConcurrencyCutUVCL, ConcurrencyCutDFG
from pm4py.algo.discovery.inductive.cuts.loop import LoopCutUVCL, LoopCutDFG
from pm4py.algo.discovery.inductive.cuts.sequence import StrictSequenceCutUVCL, StrictSequenceCutDFG
from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceCutUVCL, ExclusiveChoiceCutDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.instances import IMInstance


class CutFactory:

    @classmethod
    def get_cuts(cls, obj: IMDataStructure, inst: IMInstance) -> List[Cut]:
        if inst is IMInstance.IM:
            if type(obj) is IMDataStructureUVCL:
                return [ExclusiveChoiceCutUVCL, StrictSequenceCutUVCL, ConcurrencyCutUVCL, LoopCutUVCL]
        if inst is IMInstance.IMd:
            if type(obj) is IMDataStructureDFG:
                return [ExclusiveChoiceCutDFG, StrictSequenceCutDFG, ConcurrencyCutDFG, LoopCutDFG]
        return list()

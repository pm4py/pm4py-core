from multiprocessing import Pool, Manager
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL
from pm4py.objects.dfg.obj import DFG
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG


class FlowerModelUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        return not EmptyTracesUVCL.holds(obj)

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        log = obj.data_structure
        uvcl_do = UVCL()
        for a in comut.get_alphabet(log):
            uvcl_do[(a,)] = 1
        uvcl_redo = UVCL()
        im_uvcl_do = IMDataStructureUVCL(uvcl_do)
        im_uvcl_redo = IMDataStructureUVCL(uvcl_redo)
        return ProcessTree(operator=Operator.LOOP), [im_uvcl_do, im_uvcl_redo]


class FlowerModelDFG(FallThrough[IMDataStructureDFG]):
    @classmethod
    def holds(cls, obj: IMDataStructureDFG) -> bool:
        return True

    @classmethod
    def apply(cls, obj: IMDataStructureDFG, pool: Pool = None, manager: Manager = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureDFG]]]:
        activities = set(obj.dfg.start_activities).union(set(obj.dfg.end_activities)).union(set(x[0] for x in obj.dfg.graph)).union(set(x[1] for x in obj.dfg.graph))
        dfg_do = DFG()
        for a in activities:
            dfg_do.start_activities[a] = 1
            dfg_do.end_activities[a] = 1
        dfg_redo = DFG()
        im_dfg_do = IMDataStructureDFG(InductiveDFG(dfg_do))
        im_dfg_redo = IMDataStructureDFG(InductiveDFG(dfg_redo))
        return ProcessTree(operator=Operator.LOOP), [im_dfg_do, im_dfg_redo]


from collections import Counter
from multiprocessing import Pool, Manager
from typing import Tuple, List, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.objects.dfg.obj import DFG
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG


class EmptyTracesUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        if cls.holds(obj):
            del obj.data_structure[()]
            return ProcessTree(operator=Operator.XOR), [IMDataStructureUVCL(Counter()),
                                                        IMDataStructureUVCL(obj.data_structure)]
        else:
            return None

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        return len(list(filter(lambda t: len(t) == 0, obj.data_structure))) > 0


class EmptyTracesDFG(FallThrough[IMDataStructureDFG]):
    @classmethod
    def apply(cls, obj: IMDataStructureDFG, pool: Pool = None, manager: Manager = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureDFG]]]:
        if cls.holds(obj):
            return ProcessTree(operator=Operator.XOR), [IMDataStructureDFG(InductiveDFG(DFG())),
                                                        IMDataStructureDFG(InductiveDFG(obj.data_structure.dfg))]
        return None

    @classmethod
    def holds(cls, obj: IMDataStructureDFG) -> bool:
        return obj.data_structure.skip

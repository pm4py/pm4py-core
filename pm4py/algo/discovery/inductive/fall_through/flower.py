from collections import Counter
from multiprocessing import Pool, Manager
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
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
        loop = ProcessTree(operator=Operator.LOOP)
        xor = ProcessTree(operator=Operator.XOR)
        skip = ProcessTree()
        loop.children.append(xor)
        loop.children.append(skip)
        xor.parent = loop
        skip.parent = loop
        for a in comut.get_alphabet(log):
            act_leaf = ProcessTree(label=a)
            act_leaf.parent = xor
            xor.children.append(act_leaf)
        return loop, []


class FlowerModelDFG(FallThrough[IMDataStructureDFG]):
    @classmethod
    def holds(cls, obj: IMDataStructureDFG) -> bool:
        return True

    @classmethod
    def apply(cls, obj: IMDataStructureDFG, pool: Pool = None, manager: Manager = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureDFG]]]:
        activities = set(obj.dfg.start_activities).union(set(obj.dfg.end_activities)).union(set(x[0] for x in obj.dfg.graph)).union(set(x[1] for x in obj.dfg.graph))
        loop = ProcessTree(operator=Operator.LOOP)
        xor = ProcessTree(operator=Operator.XOR)
        skip = ProcessTree()
        loop.children.append(xor)
        loop.children.append(skip)
        xor.parent = loop
        skip.parent = loop
        for a in activities:
            act_leaf = ProcessTree(label=a)
            act_leaf.parent = xor
            xor.children.append(act_leaf)
        return loop, []

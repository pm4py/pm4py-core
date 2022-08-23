from collections import Counter
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut


class FlowerModelUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        return not EmptyTracesUVCL.holds(obj)

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        log = obj.data_structure
        logs = [IMDataStructureUVCL(Counter({(a,): 1})) for a in comut.get_alphabet(log)]
        logs.append(IMDataStructureUVCL(Counter()))
        return ProcessTree(operator=Operator.LOOP), logs

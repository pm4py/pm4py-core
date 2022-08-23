from collections import Counter
from typing import Tuple, List, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator


class EmptyTracesUVCL(FallThrough[IMDataStructureUVCL]):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        if cls.holds(obj):
            del obj.data_structure[()]
            return ProcessTree(operator=Operator.XOR), [IMDataStructureUVCL(Counter()),
                                                        IMDataStructureUVCL(obj.data_structure)]
        else:
            return None

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL) -> bool:
        return len(list(filter(lambda t: len(t) == 0, obj.data_structure))) > 0

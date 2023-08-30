from collections import Counter
from multiprocessing import Pool, Manager
from typing import Tuple, List, Optional, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.objects.powl.obj import OperatorPOWL
from pm4py.objects.process_tree.obj import Operator
from copy import copy


class POWLEmptyTracesUVCL(EmptyTracesUVCL):

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None,
              parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[OperatorPOWL, List[IMDataStructureUVCL]]]:
        if cls.holds(obj, parameters):
            data_structure = copy(obj.data_structure)
            del data_structure[()]
            return OperatorPOWL(Operator.XOR, []), [IMDataStructureUVCL(Counter()),
                                                        IMDataStructureUVCL(data_structure)]
        else:
            return None

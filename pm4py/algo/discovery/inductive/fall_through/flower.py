from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTraces
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression.dtypes import UCL
from pm4py.util.compression import util as comut


class FlowerModel(FallThrough[UCL]):

    @classmethod
    def holds(cls, log: UCL) -> bool:
        return not EmptyTraces.holds(log)

    @classmethod
    def apply(cls, log: UCL) -> Optional[Tuple[ProcessTree, List[UCL]]]:
        return ProcessTree(operator=Operator.LOOP), [[a] for a in comut.get_alphabet(log)]


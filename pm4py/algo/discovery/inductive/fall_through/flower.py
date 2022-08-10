from collections import Counter
from typing import Optional, Tuple, List

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTraces
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class FlowerModel(FallThrough[UVCL]):

    @classmethod
    def holds(cls, log: UVCL) -> bool:
        return not EmptyTraces.holds(log)

    @classmethod
    def apply(cls, log: UVCL) -> Optional[Tuple[ProcessTree, List[UVCL]]]:
        l = [Counter({(a,): 1}) for a in comut.get_alphabet(log)]
        l.append(Counter())
        return ProcessTree(operator=Operator.LOOP), l

from collections import Counter
from typing import Tuple, List, Optional

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression.dtypes import UVCL


class EmptyTraces(FallThrough[UVCL]):

    @classmethod
    def apply(cls, log: UVCL) -> Optional[Tuple[ProcessTree, List[UVCL]]]:
        if cls.holds(log):
            del log[()]
            return ProcessTree(operator=Operator.XOR), [Counter(), log]
        else:
            return None

    @classmethod
    def holds(cls, log: UVCL) -> bool:
        return len(list(filter(lambda t: len(t) == 0, log))) > 0

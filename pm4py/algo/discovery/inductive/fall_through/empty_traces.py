from typing import Tuple, List, Optional

from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough, T
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression.dtypes import UCL


class EmptyTraces(FallThrough[UCL]):

    @classmethod
    def apply(cls, log: UCL) -> Optional[Tuple[ProcessTree, List[UCL]]]:
        return ProcessTree(operator=Operator.XOR), [[], list(filter(lambda t: len(t) > 0, log))] if cls.holds(
            log) else None

    @classmethod
    def holds(cls, log: UCL) -> bool:
        return len(list(filter(lambda t: len(t) == 0, log))) > 0

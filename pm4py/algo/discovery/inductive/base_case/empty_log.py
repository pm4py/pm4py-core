from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UVCL


class EmptyLogBaseCase(BaseCase[UVCL]):
    @classmethod
    def holds(cls, obj=UVCL) -> bool:
        return len(obj) == 0

    @classmethod
    def leaf(cls, obj=UVCL) -> ProcessTree:
        return ProcessTree()

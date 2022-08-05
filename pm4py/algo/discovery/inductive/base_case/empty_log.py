from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UCL


class EmptyLogBaseCase(BaseCase[UCL]):
    @classmethod
    def applies(cls, obj=UCL) -> bool:
        return len(obj) == 0

    @classmethod
    def get_leaf(cls, obj=UCL) -> ProcessTree:
        return ProcessTree()

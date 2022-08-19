from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class SingleActivityBaseCase(BaseCase[UVCL]):
    @classmethod
    def holds(cls, obj=UVCL) -> bool:
        if len(obj.keys()) != 1:
            return False
        if len(list(obj.keys())[0]) > 1:
            return False
        return True

    @classmethod
    def leaf(cls, obj=UVCL) -> ProcessTree:
        for t in obj:
            return ProcessTree(label=t[0])

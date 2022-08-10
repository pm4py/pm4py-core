from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class SingleActivityBaseCase(BaseCase[UVCL]):
    @classmethod
    def holds(cls, obj=UVCL) -> bool:
        return len(obj.keys()) == 1 and len(comut.get_alphabet(obj)) == 1

    @classmethod
    def leaf(cls, obj=UVCL) -> ProcessTree:
        for t in obj:
            return ProcessTree(label=t[0])

from typing import Optional

from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UCL
from pm4py.util.compression import util as comut


class SingleActivity(BaseCase[UCL]):
    @classmethod
    def applies(cls, obj=UCL) -> bool:
        return len(list(filter(lambda t: len(t) == 1, obj))) == len(obj) and len(
            comut.get_alphabet(obj)) == 1

    @classmethod
    def leaf(cls, obj=UCL) -> ProcessTree:
        return ProcessTree(label=obj[0][0])

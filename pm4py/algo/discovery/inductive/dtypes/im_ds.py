from abc import ABC
from typing import TypeVar, Generic

from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL

T = TypeVar('T')


class IMDataStructure(ABC, Generic[T]):
    """
    The IMDataStructure is a helper class that unifies all possible data structures (typically logs or dfgs) that can
    be used for the classical Inductive Miner. The generic TypeVar 'T' is supposed to be the underlying data object
    used, and, should always be able to construct a DFG object. For example, T can be a dataframe, some other
    object representing an event log or a DFG itself.
    """

    def __init__(self, obj: T):
        self._obj = obj

    @property
    def dfg(self) -> DFG:
        pass

    @property
    def data_structure(self) -> T:
        return self._obj


class IMDataStructureLog(IMDataStructure[T], ABC, Generic[T]):
    """
    Generic class intended to represent that any subclass carries information that is captured in an event log.
    """


class IMDataStructureUVCL(IMDataStructureLog[UVCL]):
    """
    Log-Based data structure class that represents the event log as a 'Univariate Variant Compressed Log (UVCL)'
    """

    def __init__(self, obj: UVCL):
        super().__init__(obj)
        self._dfg = comut.discover_dfg_uvcl(self._obj)

    @property
    def dfg(self) -> DFG:
        return self._dfg


class IMDataStructureDFG(IMDataStructure[InductiveDFG]):
    """
    DFG-Based data structure class
    """

    @property
    def dfg(self) -> DFG:
        return self._obj.dfg

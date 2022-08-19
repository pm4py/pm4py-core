from abc import abstractmethod
from typing import TypeVar, Generic

from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL

T = TypeVar('T')


class IMDataStructure(Generic[T]):

    def __init__(self, obj: T):
        self._obj = obj

    @abstractmethod
    def get_dfg(self) -> DFG:
        pass

    @property
    def data_structure(self):
        return self._obj


class IMUVCLDataStructure(IMDataStructure[UVCL]):
    def get_dfg(self) -> DFG:
        return comut.discover_dfg_uvcl(self._obj)

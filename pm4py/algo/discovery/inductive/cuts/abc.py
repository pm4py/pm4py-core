from abc import ABC, abstractmethod
from typing import Optional, List, Collection, Any, Union, Tuple, Generic, TypeVar

from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression.util import UCL

T = TypeVar('T', bound=Union[UCL, DFG])


class Cut(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def get_operator(cls) -> Operator:
        pass

    @classmethod
    @abstractmethod
    def detect(cls, dfg: DFG, log: UCL = None) -> Optional[List[Collection[Any]]]:
        pass

    @classmethod
    @abstractmethod
    def project(cls, obj: T, groups: List[Collection[Any]]) -> List[T]:
        pass

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union, Tuple, List, Optional

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UVCL

T = TypeVar('T', bound=Union[UVCL, DFG])


class FallThrough(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def holds(cls, t: T) -> bool:
        pass

    @classmethod
    @abstractmethod
    def apply(cls, t: T) -> Optional[Tuple[ProcessTree, List[T]]]:
        pass

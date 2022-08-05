from abc import ABC, abstractmethod
from typing import Union, TypeVar, Generic, Optional

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UCL

T = TypeVar('T', bound=Union[UCL, DFG])


class BaseCase(ABC, Generic[T]):

    @classmethod
    def apply(cls, obj=T) -> Optional[ProcessTree]:
        return cls.leaf(obj) if cls.applies(obj) else None

    @classmethod
    @abstractmethod
    def applies(cls, obj=T) -> bool:
        pass

    @classmethod
    @abstractmethod
    def leaf(cls, obj=T) -> ProcessTree:
        pass

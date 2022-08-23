from abc import ABC, abstractmethod
from typing import Union, TypeVar, Generic, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=Union[IMDataStructure])


class BaseCase(ABC, Generic[T]):

    @classmethod
    def apply(cls, obj=T) -> Optional[ProcessTree]:
        return cls.leaf(obj) if cls.holds(obj) else None

    @classmethod
    @abstractmethod
    def holds(cls, obj=T) -> bool:
        pass

    @classmethod
    @abstractmethod
    def leaf(cls, obj=T) -> ProcessTree:
        pass

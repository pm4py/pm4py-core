from abc import ABC, abstractmethod
from typing import Optional, List, Collection, Any, Tuple, Generic, TypeVar

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)


class Cut(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def operator(cls) -> ProcessTree:
        pass

    @classmethod
    @abstractmethod
    def holds(cls, obj: T) -> Optional[List[Collection[Any]]]:
        pass

    @classmethod
    def apply(cls, obj: T) -> Optional[Tuple[ProcessTree, List[T]]]:
        g = cls.holds(obj)
        return (cls.operator(), cls.project(obj, g)) if g is not None else g

    @classmethod
    @abstractmethod
    def project(cls, obj: T, groups: List[Collection[Any]]) -> List[T]:
        """
        Projection of the given data object (Generic type T).
        Returns a corresponding process tree and the projected sub logs according to the identified groups.
        A precondition of the project function is that it holds on the object for the given Object
        """
        pass

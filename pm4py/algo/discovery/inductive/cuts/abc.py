from abc import ABC, abstractmethod
from typing import Optional, List, Collection, Any, Union, Tuple, Generic, TypeVar

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.compression.dtypes import UCL

T = TypeVar('T', bound=Union[UCL, DFG])


class Cut(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def operator(cls) -> ProcessTree:
        pass

    @classmethod
    @abstractmethod
    def holds(cls, obj: T, dfg: DFG = None) -> Optional[List[Collection[Any]]]:
        pass

    @classmethod
    def apply(cls, obj: T, dfg: DFG = None) -> Optional[Tuple[ProcessTree, List[T]]]:
        g = cls.holds(obj, dfg)
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

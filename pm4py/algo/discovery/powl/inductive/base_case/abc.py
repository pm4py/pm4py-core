from abc import ABC, abstractmethod
from typing import Union, TypeVar, Generic, Optional, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.powl.obj import POWL

T = TypeVar('T', bound=Union[IMDataStructure])


class BaseCase(ABC, Generic[T]):

    @classmethod
    def apply(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> Optional[POWL]:
        return cls.leaf(obj, parameters) if cls.holds(obj, parameters) else None

    @classmethod
    @abstractmethod
    def holds(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> bool:
        pass

    @classmethod
    @abstractmethod
    def leaf(cls, obj=T, parameters: Optional[Dict[str, Any]] = None) -> POWL:
        pass

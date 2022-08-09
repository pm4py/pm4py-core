from abc import abstractmethod
from enum import Enum
from typing import Optional, Tuple, Collection, Any, List, TypeVar, Generic, Union

from pm4py.objects.dfg.obj import DFG
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import constants
from pm4py.util.compression.dtypes import UCL


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


T = TypeVar('T', bound=Union[UCL, DFG])


class InductiveMinerFramework(Generic[T]):

    @abstractmethod
    def apply_base_case(self, obj: T) -> Optional[ProcessTree]:
        pass

    @abstractmethod
    def find_cut(self, obj: T) -> Optional[Tuple[ProcessTree, List[Collection[Any]]]]:
        pass

    @abstractmethod
    def fall_through(self, obj: T):
        pass

    @abstractmethod
    def apply(self, obj: T) -> ProcessTree:
        pass

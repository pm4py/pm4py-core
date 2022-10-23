'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from abc import ABC, abstractmethod
from typing import Optional, List, Collection, Any, Tuple, Generic, TypeVar, Dict

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)


class Cut(ABC, Generic[T]):

    @classmethod
    @abstractmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        pass

    @classmethod
    @abstractmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
        pass

    @classmethod
    def apply(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[ProcessTree, List[T]]]:
        g = cls.holds(obj, parameters)
        return (cls.operator(), cls.project(obj, g, parameters)) if g is not None else g

    @classmethod
    @abstractmethod
    def project(cls, obj: T, groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Projection of the given data object (Generic type T).
        Returns a corresponding process tree and the projected sub logs according to the identified groups.
        A precondition of the project function is that it holds on the object for the given Object
        """
        pass

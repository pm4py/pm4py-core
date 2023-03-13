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
import os
from abc import abstractmethod, ABC
from typing import Optional, Tuple, List, TypeVar, Generic, Dict, Any

from pm4py.algo.discovery.inductive.base_case.factory import BaseCaseFactory
from pm4py.algo.discovery.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.algo.discovery.inductive.fall_through.factory import FallThroughFactory
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree
from enum import Enum
from pm4py.util import exec_utils, constants


T = TypeVar('T', bound=IMDataStructure)


class Parameters(Enum):
    MULTIPROCESSING = "multiprocessing"


class InductiveMinerFramework(ABC, Generic[T]):
    """
    Base Class Implementing the Inductive Miner Framework.
    How to Extend:
    1. Create a dedicated IMDataStructure class (see pm4py.algo.discovery.inductive.dtypes.im_ds.py)
    2. Create dedicated Base Cases, Cuts and Fall Throughs for the newly constructed IMDataStructure
    3. Extend the BaseCaseFactory, CutFactory and FallThroughFactory with the newly created functions
    4. Create a subclass of this class indicating the type on which it is defined and the corresponding IMInstance.
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        if parameters is None:
            parameters = {}

        enable_multiprocessing = exec_utils.get_param_value(Parameters.MULTIPROCESSING, parameters, constants.ENABLE_MULTIPROCESSING_DEFAULT)

        if enable_multiprocessing:
            from multiprocessing import Pool, Manager

            self._pool = Pool(os.cpu_count() - 1)
            self._manager = Manager()
            self._manager.support_list = []
        else:
            self._pool = None
            self._manager = None

    def apply_base_cases(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[ProcessTree]:
        return BaseCaseFactory.apply_base_cases(obj, self.instance(), parameters=parameters)

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[ProcessTree, List[T]]]:
        return CutFactory.find_cut(obj, self.instance(), parameters=parameters)

    def fall_through(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Tuple[ProcessTree, List[T]]:
        return FallThroughFactory.fall_through(obj, self.instance(), self._pool, self._manager, parameters=parameters)

    def apply(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        tree = self.apply_base_cases(obj, parameters)
        if tree is None:
            cut = self.find_cut(obj, parameters)
            if cut is not None:
                tree = self._recurse(cut[0], cut[1], parameters=parameters)
        if tree is None:
            ft = self.fall_through(obj, parameters)
            tree = self._recurse(ft[0], ft[1], parameters=parameters)
        return tree

    def _recurse(self, tree: ProcessTree, objs: List[T], parameters: Optional[Dict[str, Any]] = None):
        children = [self.apply(obj, parameters=parameters) for obj in objs]
        for c in children:
            c.parent = tree
        tree.children.extend(children)
        return tree

    @abstractmethod
    def instance(self) -> IMInstance:
        pass

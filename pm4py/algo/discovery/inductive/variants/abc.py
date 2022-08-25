import os
from abc import abstractmethod, ABC
from multiprocessing import Pool, Manager
from typing import Optional, Tuple, List, TypeVar, Generic

from pm4py.algo.discovery.inductive.base_case.factory import BaseCaseFactory
from pm4py.algo.discovery.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure
from pm4py.algo.discovery.inductive.fall_through.factory import FallThroughFactory
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)


class InductiveMinerFramework(ABC, Generic[T]):
    """
    Base Class Implementing the Inductive Miner Framework.
    How to Extend:
    1. Create a dedicated IMDataStructure class (see pm4py.algo.discovery.inductive.dtypes.im_ds.py)
    2. Create dedicated Base Cases, Cuts and Fall Throughs for the newly constructed IMDataStructure
    3. Extend the BaseCaseFactory, CutFactory and FallThroughFactory with the newly created functions
    4. Create a subclass of this class indicating the type on which it is defined and the corresponding IMInstance.
    """

    def __init__(self):
        self._pool = Pool(os.cpu_count() - 1)
        self._manager = Manager()

    def apply_base_case(self, obj: T) -> Optional[ProcessTree]:
        for b in BaseCaseFactory.get_base_cases(obj, self.instance()):
            r = b.apply(obj)
            if r is not None:
                return r
        return None

    def find_cut(self, obj: T) -> Optional[Tuple[ProcessTree, List[T]]]:
        for c in CutFactory.get_cuts(obj, self.instance()):
            r = c.apply(obj)
            if r is not None:
                return r
        return None

    def fall_through(self, obj: T) -> Optional[Tuple[ProcessTree, List[T]]]:
        for f in FallThroughFactory.get_fall_throughs(obj, self.instance()):
            r = f.apply(obj, self._pool, self._manager)
            if r is not None:
                return r
        return None

    def apply(self, obj: T) -> ProcessTree:
        tree = self.apply_base_case(obj)
        if tree is None:
            cut = self.find_cut(obj)
            if cut is not None:
                tree = self._recurse(cut[0], cut[1])
        if tree is None:
            ft = self.fall_through(obj)
            tree = self._recurse(ft[0], ft[1])
        return tree

    def _recurse(self, tree: ProcessTree, objs: List[T]):
        children = [self.apply(obj) for obj in objs]
        for c in children:
            c.parent = tree
        tree.children.extend(children)
        return tree

    @abstractmethod
    def instance(self) -> IMInstance:
        pass

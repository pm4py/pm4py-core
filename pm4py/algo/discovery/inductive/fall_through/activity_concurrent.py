from collections import Counter
from multiprocessing import Pool, Queue, Manager, Event
from typing import Optional, Tuple, List, Any, Dict

from pm4py.algo.discovery.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL


class ActivityConcurrentUVCL(FallThrough[IMDataStructureUVCL]):
    MULTI_PROCESSING_LOWER_BOUND = 20

    @classmethod
    def _process_candidate(cls, c: Any, log: UVCL, queue: Queue = None, ev: Event = None, parameters: Optional[Dict[str, Any]] = None):
        l_alt = Counter()
        for t in log:
            l_alt[tuple(filter(lambda e: e != c, t))] = log[t]
        cut = cls._find_cut(IMDataStructureUVCL(l_alt), ev, parameters=parameters)
        if queue is not None:
            queue.put((c, cut))
        return cut if cut is not None else None

    @classmethod
    def _get_candidate(cls, obj: IMDataStructureUVCL, pool: Pool, manager: Manager, parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        log = obj.data_structure
        candidates = comut.get_alphabet(log)
        if len(candidates) > 2:
            if pool is not None and manager is not None and len(
                    candidates) > ActivityConcurrentUVCL.MULTI_PROCESSING_LOWER_BOUND:
                q = manager.Queue()
                ev = manager.Event()
                # avoid dangerous freealloc from Python's garbage collector
                manager.support_list.append(q)
                manager.support_list.append(ev)

                for a in candidates:
                    pool.apply_async(cls._process_candidate, (a, log, q, ev, parameters))
                potentials = set(candidates)
                while len(potentials) > 0:
                    (c, cut) = q.get(block=True)
                    if cut is None:
                        potentials.remove(c)
                    else:
                        ev.set()
                        return c
            else:
                for a in candidates:
                    cut = cls._process_candidate(a, log, parameters=parameters)
                    if cut is not None:
                        return a
        return None

    @classmethod
    def _find_cut(cls, obj: IMDataStructureUVCL, ev: Event, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        for c in CutFactory.get_cuts(obj, IMInstance.IM, parameters=parameters):
            if ev is not None and ev.is_set():
                return None
            r = c.apply(obj, parameters)
            if r is not None:
                return r
        return None

    @classmethod
    def holds(cls, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> bool:
        return cls._get_candidate(obj, None, None, parameters) is not None

    @classmethod
    def apply(cls, obj: IMDataStructureUVCL, pool: Pool = None, manager: Manager = None, parameters: Optional[Dict[str, Any]] = None) -> Optional[
        Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
        candidate = cls._get_candidate(obj, pool, manager, parameters)
        if candidate is None:
            return None
        log = obj.data_structure
        l_a = Counter()
        l_other = Counter()
        for t in log:
            l_a.update({tuple(filter(lambda e: e == candidate, t)): log[t]})
            l_other.update({tuple(filter(lambda e: e != candidate, t)): log[t]})
        return ProcessTree(operator=Operator.PARALLEL), [IMDataStructureUVCL(l_a), IMDataStructureUVCL(l_other)]

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
from collections import Counter
from typing import Optional, Tuple, List, Any, Dict

from pm4py.algo.discovery.inductive.cuts.factory import CutFactory
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.abc import FallThrough
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL
from enum import Enum
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    MULTIPROCESSING = "multiprocessing"


class ActivityConcurrentUVCL(FallThrough[IMDataStructureUVCL]):
    MULTI_PROCESSING_LOWER_BOUND = 20

    @classmethod
    def _process_candidate(cls, c: Any, log: UVCL, queue=None, ev=None, parameters: Optional[Dict[str, Any]] = None):
        l_alt = Counter()
        for t in log:
            l_alt[tuple(filter(lambda e: e != c, t))] = log[t]
        cut = cls._find_cut(IMDataStructureUVCL(l_alt), ev, parameters=parameters)
        if queue is not None:
            queue.put((c, cut))
        return cut if cut is not None else None

    @classmethod
    def _get_candidate(cls, obj: IMDataStructureUVCL, pool, manager, parameters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        if parameters is None:
            parameters = {}

        enable_multiprocessing = exec_utils.get_param_value(Parameters.MULTIPROCESSING, parameters, constants.ENABLE_MULTIPROCESSING_DEFAULT)

        log = obj.data_structure
        candidates = sorted(list(comut.get_alphabet(log)))
        if pool is None or manager is None or not enable_multiprocessing or len(candidates) <= ActivityConcurrentUVCL.MULTI_PROCESSING_LOWER_BOUND:
            for a in candidates:
                cut = cls._process_candidate(a, log, parameters=parameters)
                if cut is not None:
                    return a
        else:
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

        return None

    @classmethod
    def _find_cut(cls, obj: IMDataStructureUVCL, ev, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[ProcessTree, List[IMDataStructureUVCL]]]:
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
    def apply(cls, obj: IMDataStructureUVCL, pool=None, manager=None, parameters: Optional[Dict[str, Any]] = None) -> Optional[
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

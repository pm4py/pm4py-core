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

from typing import List, Optional, Dict, Any, Tuple, Type

from pm4py.algo.discovery.powl.inductive.cuts.concurrency import POWLConcurrencyCutUVCL
from pm4py.algo.discovery.powl.inductive.cuts.factory import S, T, CutFactory
from pm4py.algo.discovery.powl.inductive.cuts.loop import POWLLoopCutUVCL
from pm4py.algo.discovery.powl.inductive.cuts.sequence import POWLStrictSequenceCutUVCL
from pm4py.algo.discovery.powl.inductive.cuts.xor import POWLExclusiveChoiceCutUVCL
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.powl.inductive.variants.brute_force.bf_partial_order_cut import BruteForcePartialOrderCutUVCL
from pm4py.objects.powl.obj import POWL


class CutFactoryPOWLBruteForce(CutFactory):

    @classmethod
    def get_cuts(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> List[Type[S]]:
        if type(obj) is IMDataStructureUVCL:
            return [POWLExclusiveChoiceCutUVCL, POWLStrictSequenceCutUVCL, POWLConcurrencyCutUVCL, POWLLoopCutUVCL,
                    BruteForcePartialOrderCutUVCL]
        return list()

    @classmethod
    def find_cut(cls, obj: IMDataStructureUVCL, parameters: Optional[Dict[str, Any]] = None) -> Optional[
            Tuple[POWL, List[T]]]:
        for c in CutFactoryPOWLBruteForce.get_cuts(obj):
            r = c.apply(obj, parameters)
            if r is not None:
                return r
        return None

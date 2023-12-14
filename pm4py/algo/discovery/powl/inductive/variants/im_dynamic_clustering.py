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
from typing import Optional, Tuple, List, TypeVar, Dict, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureLog
from pm4py.algo.discovery.powl.inductive.variants.dynamic_clustering.factory import CutFactoryPOWLDynamicClustering
from pm4py.algo.discovery.powl.inductive.variants.im_tree import IMBasePOWL
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import POWL

T = TypeVar('T', bound=IMDataStructureLog)


class POWLInductiveMinerDynamicClustering(IMBasePOWL):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.DYNAMIC_CLUSTERING

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        res = CutFactoryPOWLDynamicClustering.find_cut(obj, parameters=parameters)
        return res

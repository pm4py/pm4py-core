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

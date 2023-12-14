from typing import Optional, Tuple, List, Dict, Any

from pm4py.algo.discovery.powl.inductive.variants.maximal.factory import CutFactoryPOWLMaximal
from pm4py.algo.discovery.powl.inductive.variants.im_tree import IMBasePOWL, T
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import POWL


class POWLInductiveMinerMaximalOrder(IMBasePOWL):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.MAXIMAL

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        res = CutFactoryPOWLMaximal.find_cut(obj, parameters=parameters)
        return res

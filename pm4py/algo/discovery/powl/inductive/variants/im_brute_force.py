from typing import Optional, Tuple, List, Dict, Any

from pm4py.algo.discovery.powl.inductive.variants.brute_force.factory import CutFactoryPOBF
from pm4py.algo.discovery.powl.inductive.variants.im_base import IMBasePOWL, T
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.powl.obj import POWL


class BruteForcePOWL(IMBasePOWL):

    def instance(self) -> POWLDiscoveryVariant:
        return POWLDiscoveryVariant.BRUTE_FORCE

    def find_cut(self, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[POWL, List[T]]]:
        res = CutFactoryPOBF.find_cut(obj, self.instance(), parameters=parameters)
        return res



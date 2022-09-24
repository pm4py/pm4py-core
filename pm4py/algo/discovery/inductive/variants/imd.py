from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance


class IMD(InductiveMinerFramework[IMDataStructureDFG]):

    def instance(self) -> IMInstance:
        return IMInstance.IMd

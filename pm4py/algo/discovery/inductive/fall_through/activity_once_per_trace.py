import copy
from typing import Collection, Any

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.algo.discovery.inductive.fall_through.activity_concurrent import ActivityConcurrentUVCL
from pm4py.util.compression import util as comut


class ActivityOncePerTraceUVCL(ActivityConcurrentUVCL):

    @classmethod
    def _get_candidates(cls, obj: IMDataStructureUVCL) -> Collection[Any]:
        candidates = copy.copy(comut.get_alphabet(obj.data_structure))
        for t in obj.data_structure:
            cc = [x for x in candidates]
            for candi in cc:
                if len(list(filter(lambda e: e == candi, t))) != 1:
                    candidates.remove(candi)
            if len(candidates) == 0:
                return candidates
        return candidates

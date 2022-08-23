from pm4py.algo.discovery.inductive.base_case.abc import BaseCase
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.objects.process_tree.obj import ProcessTree


class SingleActivityBaseCaseUVCL(BaseCase[IMDataStructureUVCL]):
    @classmethod
    def holds(cls, obj=IMDataStructureUVCL) -> bool:
        if len(obj.data_structure.keys()) != 1:
            return False
        if len(list(obj.data_structure.keys())[0]) > 1:
            return False
        return True

    @classmethod
    def leaf(cls, obj=IMDataStructureUVCL) -> ProcessTree:
        for t in obj.data_structure:
            return ProcessTree(label=t[0])


class SingleActivityBaseCaseDFG(BaseCase[IMDataStructureDFG]):

    @classmethod
    def holds(cls, obj=IMDataStructureDFG) -> bool:
        return len(obj.dfg.graph) == 0 and len(set(obj.dfg.start_activities).union(obj.dfg.end_activities)) == 0

    @classmethod
    def leaf(cls, obj=IMDataStructureDFG) -> ProcessTree:
        return ProcessTree(label=list(obj.dfg.start_activities)[0])

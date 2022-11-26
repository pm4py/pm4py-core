from pm4py.objects.dfg.obj import DFG


class InductiveDFG:

    def __init__(self, dfg: DFG, skip: bool = False):
        self._dfg = dfg
        self._skip = skip

    @property
    def dfg(self) -> DFG:
        return self._dfg

    @property
    def skip(self) -> bool:
        return self._skip

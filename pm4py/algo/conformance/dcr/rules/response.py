from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from typing import Union
from pm4py.objects.dcr.obj import DcrGraph
from typing import List, Tuple, Any

class CheckResponse(CheckFrame):
    @classmethod
    def check_rule(cls, graph: DcrGraph, responses: List[Tuple[str, str]], deviations: List[Tuple[str, Any]]):
        """
        Checks if event violates the response relation.

        If DCR Graph contains pending events, the Graph has not done an incomplete run, as events are waiting to be executed

        Parameters
        --------------
        graph: DcrGraph
            DCR graph
        responses:
            responses not yet executed
        deviations: List[Tuple[str, Any]]
            List of deviations

        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        """
        # if activities are pending, and included, thats a response violation
        if graph.marking.included.intersection(graph.marking.pending):
            for pending in responses:
                deviations.append(('responseViolation', tuple(pending)))
        return deviations

from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from typing import Union
from pm4py.objects.dcr.obj import DCR_Graph
from typing import List, Tuple, Any

class CheckResponse(CheckFrame):
    @classmethod
    def check_rule(cls, G: DCR_Graph, responses: List[Tuple[str, str]], deviations: List[Tuple[str, Any]]):
        """
        Checks if event violates the response relation.

        If DCR Graph contains pending events, the Graph has not done an incomplete run, as events are waiting to be executed

        Parameters
        --------------
        G: DCR_Graph
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
        if G.marking.included.intersection(G.marking.pending):
            for pending in responses:
                deviations.append(('responseViolation', tuple(pending)))
        return deviations

from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.obj import DCR_Graph
from typing import List, Tuple, Any

class CheckInclude(CheckFrame):
    @classmethod
    def check_rule(cls, e: str, G: DCR_Graph, deviations: List[Tuple[str, Any]]):
        """
        Checks if event violates the include relation

        Parameters
        --------------
        e: str
            current event
        G: DCR_Graph
            DCR Graph
        deviations: List[Tuple[str, Any]]
            List of deviations

        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        """
        if e not in G.marking.included:
            for event_prime in G.includesTo:
                if e in G.includesTo[event_prime]:
                    if ['includeViolation', (event_prime, e)] not in deviations:
                        deviations.append(('includeViolation', (event_prime, e)))
        return deviations

from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.obj import DcrGraph
from typing import List, Tuple, Any

class CheckInclude(CheckFrame):
    @classmethod
    def check_rule(cls, event: str, graph: DcrGraph, deviations: List[Tuple[str, Any]]):
        """
        Checks if event violates the include relation

        Parameters
        --------------
        event: str
            current event
        graph: DcrGraph
            DCR Graph
        deviations: List[Tuple[str, Any]]
            List of deviations

        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        """
        if event not in graph.marking.included:
            for event_prime in graph.includes:
                if event in graph.includes[event_prime]:
                    if ['includeViolation', (event_prime, event)] not in deviations:
                        deviations.append(('includeViolation', (event_prime, event)))
        return deviations

from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.obj import DcrGraph
from typing import List, Tuple, Any

class CheckCondition(CheckFrame):
    @classmethod
    def check_rule(cls, event: str, graph: DcrGraph, deviations: List[Tuple[str, Any]]):
        '''
        Checks if event violates the conditions relation

        Parameters
        --------------
        event: str
            Current event
        graph: DcrGraph
            DCR Graph
        deviations: List[Tuple[str, Any]]
            List of deviations
        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        '''
        # we check if conditions for activity has been executed, if not, that's a conditions violation
        # check if act is in conditions for
        if event in graph.conditions:
            # check the conditions for event act
            for event_prime in graph.conditions[event]:
                # if conditions are included and not executed, add violation
                if event_prime in graph.conditions[event].intersection(
                        graph.marking.included.difference(graph.marking.executed)):
                    if ('conditionViolation', (event_prime, event)) not in deviations:
                        deviations.append(('conditionViolation', (event_prime, event)))
        return deviations

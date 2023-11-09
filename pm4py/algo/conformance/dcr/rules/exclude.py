from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.obj import DcrGraph
from typing import List, Tuple, Any

class CheckExclude(CheckFrame):
    @classmethod
    def check_rule(cls, event: str, graph: DcrGraph, deviations: List[Tuple[str, Any]]):
        '''
        Checks if event violates the exclude relation

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
        # if an acitivty has been excluded, but trace tries to execute, exclude violation
        if event not in graph.marking.included:
            #if violation exist, no need to store it
            if ('excludeViolation', event) not in deviations:
                deviations.append(('excludeViolation', event))
        return deviations

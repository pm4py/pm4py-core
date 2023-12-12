from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.obj import DcrGraph
from typing import List, Tuple, Any

class CheckExclude(CheckFrame):
    @classmethod
    def check_rule(cls, event: str, graph: DcrGraph, execution_his:List, deviations: List[Tuple[str, Any]]):
        '''
        Checks if event violates the exclude relation

        Parameters
        --------------
        event: str
            Current event
        graph: DcrGraph
            DCR Graph
        execution_his: List
            List to check for when event was excluded
        deviations: List[Tuple[str, Any]]
            List of deviations
        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        '''
        # if an acitivty has been excluded, but trace tries to execute, exclude violation
        if event not in graph.marking.included:
            exclude_origin = []
            for event_prime in execution_his:
                if event in graph.excludes.get(event_prime,set()):
                    exclude_origin.append(event_prime)
                if event in graph.includes.get(event_prime,set()):
                    exclude_origin = []
            #if violation exist, no need to store it
            for event_prime in exclude_origin:
                if ('excludeViolation', (event_prime, event)) not in deviations:
                    deviations.append(('excludeViolation', (event_prime, event)))
        return deviations

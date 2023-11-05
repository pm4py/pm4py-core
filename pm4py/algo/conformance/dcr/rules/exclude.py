from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.obj import DCR_Graph
from typing import List, Tuple, Any

class CheckExclude(CheckFrame):
    @classmethod
    def check_rule(cls, e: str, G: DCR_Graph, deviations: List[Tuple[str, Any]]):
        '''
        Checks if event violates the exclude relation

        Parameters
        --------------
        e: str
            Current event
        G: DCR_Graph
            DCR Graph
        deviations: List[Tuple[str, Any]]
            List of deviations

        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        '''
        # if an acitivty has been excluded, but trace tries to execute, exclude violation
        if e not in G.marking.included:
            #if violation exist, no need to store it
            if ('excludeViolation', e) not in deviations:
                deviations.append(('excludeViolation', e))
        return deviations

from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.roles.obj import RoledcrGraph
from typing import List, Tuple, Any

class CheckRole(CheckFrame):
    @classmethod
    def check_rule(cls, event: str, graph: RoledcrGraph, role: str, deviations: List[Tuple[str, Any]]):
        '''
        Checks if event violates the role assignments
            1.) if event contain role not in model
            2.) if event in model contains roles, but executed with wrong event

        Parameters
        --------------
        event: str
            current event
        graph: RoledcrGraph
            DCR Graph
        role: str
            Role of the event
        deviations: List[Tuple[str, Any]]
            List of deviations
        Returns
        --------------
        deviations: List[Tuple[str, Any]]
            List of updated deviation if any were detected
        '''
        if role not in graph.roles and role == role:
            # if role doesn't exist, means that they do not have authority to perform the action
            if ('roleViolation', role) not in deviations:
                deviations.append(('roleViolation', role))
            return deviations
        else:
            temp = {event: set()}
            for i in graph.role_assignments:
                if event in graph.role_assignments[i]:
                    temp[event].add(i)
            # if activity has no role, return, as it can be excuted by anybody
            if not temp[event]:
                return deviations
            # if event in model has roles
            # violation when:
            # 1) when as event in model does not have role
            res = temp[event].intersection({role})
            if not res:
                if ('roleViolation', (role, event)) not in deviations:
                    deviations.append(('roleViolation', (role, event)))
            return deviations


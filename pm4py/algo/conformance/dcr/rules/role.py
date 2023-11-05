from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
from pm4py.objects.dcr.roles.obj import RoleDCR_Graph
from typing import List, Tuple, Any

class CheckRole(CheckFrame):
    @classmethod
    def check_rule(cls, e: str, G: RoleDCR_Graph, role: str, deviations: List[Tuple[str, Any]]):
        '''
        Checks if event violates the role assignments
            1.) if event contain role not in model
            2.) if event in model contains roles, but executed with wrong event

        Parameters
        --------------
        e: str
            current event
        G: RoleDCR_Graph
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
        if role not in G.roles and role == role:
            # if role doesn't exist, means that they do not have authority to perform the action
            if ('roleViolation', role) not in deviations:
                deviations.append(('roleViolation', role))
            return deviations
        else:
            temp = {e: set()}
            for i in G.roleAssignments:
                if e in G.roleAssignments[i]:
                    temp[e].add(i)
            # if activity has no role, return, as it can be excuted by anybody
            if not temp[e]:
                return deviations
            # if event in model has roles
            # violation when:
            # 1) when as event in model does not have role
            res = temp[e].intersection({role})
            if not res:
                if ('roleViolation', (role, e)) not in deviations:
                    deviations.append(('roleViolation', (role, e)))
            return deviations


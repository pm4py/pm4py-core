from pm4py.algo.conformance.dcr.rules.abc import CheckFrame


class CheckRole(CheckFrame):
    @classmethod
    def check_rule(cls, act, G, role, deviations):
        '''
        Checks if event violates the role relation
            1.) if event contain role not in model
            2.) if event in model contains roles, but executed with wrong event

        Parameters
        --------------
        act
            Activity to be checked
        G
            :class: `pm4py.objects.dcr.roles.obj.RoleDCR_Graph` the model being checked
        role
            Role of the event
        deviations
            List of deviations
        Returns
        --------------
        deviations
            List of updated deviation if any were detected
        '''
        if role not in G.roles and role == role:
            # if role doesn't exist, means that they do not have authority to perform the action
            if ['roleViolation', role] not in deviations:
                deviations.append(['roleViolation', role])
            return deviations
        else:
            temp = {act: set()}
            for i in G.roleAssignments:
                if act in G.roleAssignments[i]:
                    temp[act].add(i)
            # if activity has no role, return, as it can be excuted by anybody
            if not temp[act]:
                return deviations
            # if event in model has roles
            # violation when:
            # 1) when as event in model does not have role
            res = temp[act].intersection({role})
            if not res:
                if ['roleViolation', (role, act)] not in deviations:
                    deviations.append(['roleViolation', (role, act)])
            return deviations


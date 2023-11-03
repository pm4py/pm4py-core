from pm4py.algo.conformance.dcr.rules.abc import CheckFrame


class CheckInclude(CheckFrame):
    @classmethod
    def check_rule(cls, act, G, deviations):
        '''
        Checks if event violates the include relation

        Parameters
        --------------
        act
            Activity to be checked
        G
            :class: `pm4py.objects.dcr.roles.obj.RoleDCR_Graph` the model being checked
        deviations
            List of deviations

        Returns
        --------------
        deviations
            List of updated deviation if any were detected
        '''
        if act not in G.marking.included:
            for e in G.includesTo:
                if act in G.includesTo[e]:
                    if ['includeViolation', (e, act)] not in deviations:
                        deviations.append(['includeViolation', (e, act)])
        return deviations

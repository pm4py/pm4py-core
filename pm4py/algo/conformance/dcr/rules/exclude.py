from pm4py.algo.conformance.dcr.rules.abc import CheckFrame


class CheckExclude(CheckFrame):
    @classmethod
    def check_rule(cls, act, G, deviations):
        '''
        Checks if event violates the exclude relation

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
        # if an acitivty has been excluded, but trace tries to execute, exclude violation
        if act not in G.marking.included:
            #if violation exist, no need to store it
            if ['excludeViolation', act] not in deviations:
                deviations.append(['excludeViolation', act])
        return deviations

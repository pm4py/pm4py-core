from pm4py.algo.conformance.dcr.rules.abc import CheckFrame


class CheckResponse(CheckFrame):
    @classmethod
    def check_rule(cls, G, responses, deviations):
        '''
        Checks if event violates the response relation.
        If DCR Graph contains pending events, the Graph has not done an incomplete run


        Parameters
        --------------
        G
            :class: `pm4py.objects.dcr.roles.obj.RoleDCR_Graph` the model being checked
        responses
            responses not yet executed
        deviations
            List of deviations

        Returns
        --------------
        deviations
            List of updated deviation if any were detected
        '''
        # if activities are pending, and included, thats a response violation
        if G.marking.included.intersection(G.marking.pending):
            for pending in responses:
                deviations.append(['responseViolation', tuple(pending)])
        return deviations

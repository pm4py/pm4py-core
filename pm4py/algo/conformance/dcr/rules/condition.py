from pm4py.algo.conformance.dcr.rules.abc import CheckFrame
class CheckCondition(CheckFrame):
    @classmethod
    def check_rule(cls, act, G, deviations):
        '''
        Checks if event violates the conditions relation

        Parameters
        --------------
        act
        G

        deviations
            List of deviations
        Returns
        --------------
        list
            list of deviations
        '''
        # we check if conditions for activity has been executed, if not, that's a conditions violation
        # check if act is in conditions for
        if act in G.conditionsFor:
            # check the conditions for event act
            for e in G.conditionsFor[act]:
                # if conditions are included and not executed, add violation
                if e in G.conditionsFor[act].intersection(
                        G.marking.included.difference(G.marking.executed)):
                    if ['conditionViolation', (e, act)] not in deviations:
                        deviations.append(['conditionViolation', (e, act)])
        return deviations

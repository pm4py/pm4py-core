from pm4py.algo.alignments import versions
from pm4py.log.util import xes

'''
This python file contains a factory method to compute alignments on the basis of an event log.
The current implemented version is the state-equation-based A* version, i.e. `pm4py.algo.alignments.versions.state_equation_a_star`
'''

STATE_EQUATION_A_STAR = 'state_equation_a_star'

VERSIONS = {STATE_EQUATION_A_STAR: versions.state_equation_a_star.apply_log}

def apply(trace_log, petri_net, initial_marking, final_marking, parameters=None, activity_key=xes.DEFAULT_NAME_KEY, variant=STATE_EQUATION_A_STAR):
    return VERSIONS[variant](trace_log, petri_net, initial_marking, final_marking, parameters, activity_key)

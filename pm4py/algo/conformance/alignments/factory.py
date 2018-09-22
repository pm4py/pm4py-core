'''
This module contains the factory method

'''
from pm4py import util as pm4pyutil
from pm4py.algo.conformance.alignments import versions
from pm4py.entities.log.util import xes

VERSION_STATE_EQUATION_A_STAR = 'state_equation_a_star'
VERSIONS = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.apply}


def apply(trace, petri_net, initial_marking, final_marking,
          parameters=None,
          version=VERSION_STATE_EQUATION_A_STAR):
    if parameters is None:
        parameters = {pm4pyutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: xes.DEFAULT_NAME_KEY}
    return VERSIONS[version](trace, petri_net, initial_marking, final_marking, parameters)

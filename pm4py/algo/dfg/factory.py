from pm4py.algo.dfg import versions as dfg_versions
from pm4py.log import util

DFG_NATIVE = 'native'
DFG_FREQUENCY = 'frequency'
DFG_PERFORMANCE = 'performance'

versions = {DFG_NATIVE: dfg_versions.native.apply, DFG_FREQUENCY: dfg_versions.native.apply, DFG_PERFORMANCE: dfg_versions.performance.apply}

def apply(trace_log, parameters=None, variant=DFG_NATIVE):
    return versions[variant](trace_log, parameters)
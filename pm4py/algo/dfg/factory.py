from pm4py.algo.dfg import versions as dfg_versions
from pm4py.log import util

DFG_NATIVE = 'native'

versions = {DFG_NATIVE: dfg_versions.native.apply}

def apply(trace_log, parameters=None, variant=DFG_NATIVE):
    return versions[variant](trace_log, parameters)

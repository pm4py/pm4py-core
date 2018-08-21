from pm4py.algo.dfg import verions as dfg_versions
from pm4py.log import util

DFG_NATIVE = 'native'

versions = {DFG_NATIVE: dfg_versions.native.apply}


def apply(trace_log, activity_key=util.xes.DEFAULT_NAME_KEY, variant=DFG_NATIVE):
    return versions[variant](trace_log, activity_key)

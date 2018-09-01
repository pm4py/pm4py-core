from pm4py.algo.dfg import versions as dfg_versions
from pm4py.log import util

DFG_NATIVE = 'native'

versions = {DFG_NATIVE: dfg_versions.native.apply}


def apply(trace_log, parameters=None, activity_key=util.xes.DEFAULT_NAME_KEY, variant=DFG_NATIVE, timestamp_key="time:timestamp"):
    return versions[variant](trace_log, parameters, activity_key, timestamp_key)

from pm4py.log.util import xes as xes_util
from pm4py.algo.inductive import versions

INDUCTIVE_ONLY_DFG = 'only_dfg'
VERSIONS = {INDUCTIVE_ONLY_DFG: versions.dfg_only.apply}

VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: versions.dfg_only.apply_dfg}

def apply(log, parameters=None, activity_key=xes_util.DEFAULT_NAME_KEY, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS[variant](log, parameters, activity_key)

def apply_dfg(dfg, parameters=None, activity_key=xes_util.DEFAULT_NAME_KEY, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_DFG[variant](dfg, parameters, activity_key)
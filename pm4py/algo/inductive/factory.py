from pm4py.log.util import xes as xes_util
from pm4py.algo.inductive import versions
from pm4py import util as pmutil

INDUCTIVE_ONLY_DFG = 'only_dfg'
VERSIONS = {INDUCTIVE_ONLY_DFG: versions.dfg_only.apply}
VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: versions.dfg_only.apply_dfg}

def apply(log, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS[variant](log, parameters)

def apply_dfg(dfg, parameters=None, variant=INDUCTIVE_ONLY_DFG):
    return VERSIONS_DFG[variant](dfg, parameters)
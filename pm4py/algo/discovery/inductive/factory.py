import pandas

from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.discovery.inductive.versions.dfg import imdfa, imdfb
from pm4py.objects.log.util import general as log_util
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.conversion.log import factory as log_conversion


INDUCTIVE_ONLY_DFG = 'only_dfg'
IMDFA = 'imdfa'
IMDFB = 'imdfb'

DEFAULT_VARIANT = IMDFA

VERSIONS = {INDUCTIVE_ONLY_DFG: imdfa.apply, IMDFA: imdfa.apply, IMDFB: imdfb.apply}
VERSIONS_DFG = {INDUCTIVE_ONLY_DFG: imdfa.apply_dfg, IMDFA: imdfa.apply_dfg, IMDFB: imdfb.apply_dfg}
VERSIONS_TREE = {INDUCTIVE_ONLY_DFG: imdfa.apply_tree, IMDFA: imdfa.apply_tree, IMDFB: imdfb.apply_tree}
VERSIONS_TREE_DFG = {INDUCTIVE_ONLY_DFG: imdfa.apply_tree_dfg, IMDFA: imdfa.apply_tree_dfg, IMDFB: imdfb.apply_tree_dfg}


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE
    if isinstance(log, pandas.core.frame.DataFrame):
        dfg = df_statistics.get_dfg_graph(log, case_id_glue=parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY],
                                          activity_key=parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY],
                                          timestamp_key=parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY])
        return VERSIONS_DFG[variant](dfg, parameters=parameters)
    return VERSIONS[variant](log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters)


def apply_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_DFG[variant](dfg, parameters)


def apply_tree(log, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_TREE[variant](log, parameters)


def apply_tree_dfg(dfg, parameters=None, variant=DEFAULT_VARIANT):
    return VERSIONS_TREE_DFG[variant](dfg, parameters)

import heapq
import sys
from copy import copy

import numpy as np

import pm4py
from pm4py import util as pm4pyutil
from pm4py.algo.conformance import alignments
from pm4py.objects import petri
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py.objects.log import log as log_implementation
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.petri.synchronous_product import construct_cost_aware
from pm4py.objects.petri.utils import construct_trace_net_cost_aware
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.lp import factory as lp_solver_factory

from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_SYNC_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import DEFAULT_LP_SOLVER_VARIANT
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_NET_COSTS
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import TRACE_NET_CONSTR_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import TRACE_NET_COST_AWARE_CONSTR_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAMETER_VARIANT_DELIMITER
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import DEFAULT_VARIANT_DELIMITER
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAMETERS
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import apply_from_variants_list_petri_string

import ray

def apply_from_variants_list_ray(var_list, petri_net_string, parameters=None):
    """
    Apply the alignments from the specification of a list of variants in the log

    Parameters
    -------------
    var_list
        List of variants (for each item, the first entry is the variant itself, the second entry may be the number of cases)
    petri_net_string
        String representing the accepting Petri net

    Returns
    --------------
    dictio_alignments
        Dictionary that assigns to each variant its alignment
    """
    if parameters is None:
        parameters = {}

    res = apply_from_variants_list_petri_string(var_list, petri_net_string, parameters=parameters)
    return res

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.petri_net.utils import check_soundness
import time
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_CASEID_KEY
from pm4py.algo.conformance.antialignments import variants

class Variants(Enum):
    VERSION_DISCOUNTED_A_STAR = variants.discounted_a_star

class Parameters(Enum):
    MARKING_LIMIT = "marking_limit"
    EXPONENT = "exponent"
    EPSILON = "epsilon"
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY

DEFAULT_VARIANT = Variants.VERSION_DISCOUNTED_A_STAR
VERSION_DISCOUNTED_A_STAR = Variants.VERSION_DISCOUNTED_A_STAR

VERSIONS = {Variants.VERSION_DISCOUNTED_A_STAR}


def apply(log, petri_net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
    if parameters is None:
        parameters = {}

    return apply_log(log_converter.apply(log, parameters, log_converter.TO_EVENT_LOG), petri_net, initial_marking,
                        final_marking, parameters=parameters, variant=variant)


def apply_log(log, petri_net, initial_marking, final_marking, parameters=None, variant=DEFAULT_VARIANT):
    """
    apply antialignments to a log
    Parameters
    -----------
    log
        object of the form :class:`pm4py.log.log.EventLog` event log
    petri_net
        :class:`pm4py.objects.petri.petrinet.PetriNet` the model to use for the alignment
    initial_marking
        :class:`pm4py.objects.petri.petrinet.Marking` initial marking of the net
    final_marking
        :class:`pm4py.objects.petri.petrinet.Marking` final marking of the net
    variant
        selected variant of the algorithm
    parameters
        :class:`dict` parameters of the algorithm,

    Returns
    -----------
    """
    if parameters is None:
        parameters = dict()

    if not check_soundness.check_easy_soundness_net_in_fin_marking(petri_net, initial_marking, final_marking):
        raise Exception("Trying to apply anti-alignments on a Petri net that is not an sound net.")

    start_time = time.time()

    antialignments = exec_utils.get_variant(variant).apply(log, petri_net, initial_marking, final_marking, parameters=None)

    total_time = start_time - time.time()

    return antialignments


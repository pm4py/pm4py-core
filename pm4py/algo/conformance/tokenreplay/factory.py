from pm4py import util as pmutil
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.objects.conversion.log import factory as log_converter
from pm4py.util import xes_constants as xes_util
from pm4py.objects.petri.exporter.versions import pnml as petri_exporter
from pm4py.statistics.variants.log import get as variants_module
import multiprocessing as mp
import math

TOKEN_REPLAY = "token_replay"
VERSIONS = {TOKEN_REPLAY: token_replay.apply}
VERSIONS_MULTIPROCESSING = {TOKEN_REPLAY: token_replay.apply_variants_list_petri_string_multiprocessing}
VARIANTS_IDX = 'variants_idx'


def apply(log, net, initial_marking, final_marking, parameters=None, variant=TOKEN_REPLAY):
    """
    Factory method to apply token-based replay
    
    Parameters
    -----------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key

    variant
        Variant of the algorithm to use
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = pmutil.constants.CASE_ATTRIBUTE_GLUE
    return VERSIONS[variant](log_converter.apply(log, parameters, log_converter.TO_EVENT_LOG), net, initial_marking,
                             final_marking, parameters=parameters)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def apply_multiprocessing(log, net, initial_marking, final_marking, parameters=None, variant=TOKEN_REPLAY):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = pmutil.constants.CASE_ATTRIBUTE_GLUE

    variants_idxs = parameters[VARIANTS_IDX] if VARIANTS_IDX in parameters else None
    if variants_idxs is None:
        variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    variants_list = [[x, len(y)] for x, y in variants_idxs.items()]

    no_cores = mp.cpu_count()

    petri_net_string = petri_exporter.export_petri_as_string(net, initial_marking, final_marking)

    n = math.ceil(len(variants_list)/no_cores)

    variants_list_split = list(chunks(variants_list, n))

    # Define an output queue
    output = mp.Queue()

    processes = [mp.Process(target=VERSIONS_MULTIPROCESSING[variant](output, x, petri_net_string, parameters=parameters)) for x in variants_list_split]

    # Run processes
    for p in processes:
        p.start()

    results = []
    for p in processes:
        result = output.get()
        results.append(result)

    al_idx = {}
    for index, el in enumerate(variants_list_split):
        for index2, var_item in enumerate(el):
            variant = var_item[0]
            for trace_idx in variants_idxs[variant]:
                al_idx[trace_idx] = results[index][index2]

    replayed_cases = []
    for i in range(len(log)):
        replayed_cases.append(al_idx[i])

    return replayed_cases

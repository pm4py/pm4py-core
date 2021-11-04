import os

from pm4py import util
from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments.petri_net.variants.state_equation_a_star import Parameters
from pm4py.objects import log as log_lib
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.objects.petri_net.utils.align_utils import pretty_print_alignments


def align(trace, net, im, fm, model_cost_function, sync_cost_function):
    trace_costs = list(map(lambda e: 1000, trace))
    params = dict()
    params[util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = log_lib.util.xes.DEFAULT_NAME_KEY
    params[Parameters.PARAM_MODEL_COST_FUNCTION] = model_cost_function
    params[Parameters.PARAM_TRACE_COST_FUNCTION] = trace_costs
    params[Parameters.PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    return ali.petri_net.algorithm.apply_trace(trace, net, im, fm, parameters=params,
                                   variant=ali.petri_net.algorithm.VERSION_STATE_EQUATION_A_STAR)


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")

    # log_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes'
    # pnml_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32.pnml'

    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    model_cost_function = dict()
    sync_cost_function = dict()
    for t in net.transitions:
        if t.label is not None:
            model_cost_function[t] = 1000
            sync_cost_function[t] = 0
        else:
            model_cost_function[t] = 1

    alignments = []
    for trace in log:
        alignments.append(align(trace, net, marking, fmarking, model_cost_function, sync_cost_function))

    pretty_print_alignments(alignments)


if __name__ == '__main__':
    execute_script()

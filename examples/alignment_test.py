import os

from pm4py import util
from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_SYNC_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_COST_FUNCTION
from pm4py.objects import log as log_lib
from pm4py.objects import petri as petri
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.conversion.log import factory as log_conv


def align(trace, net, im, fm, model_cost_function, sync_cost_function):
    trace_costs = list(map(lambda e: 1000, trace))
    params = dict()
    params[util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = log_lib.util.xes.DEFAULT_NAME_KEY
    params[PARAM_MODEL_COST_FUNCTION] = model_cost_function
    params[PARAM_TRACE_COST_FUNCTION] = trace_costs
    params[PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    return ali.factory.apply_trace(trace, net, im, fm, parameters=params,
                                   version=ali.factory.VERSION_STATE_EQUATION_A_STAR)


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")

    # log_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes'
    # pnml_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32.pnml'

    log = xes_importer.import_log(log_path)
    log = log_conv.apply(log, parameters=None, variant=log_conv.TO_EVENT_STREAM)
    net, marking, fmarking = petri.importer.pnml.import_net(
        pnml_path)

    model_cost_function = dict()
    sync_cost_function = dict()
    for t in net.transitions:
        if t.label is not None:
            model_cost_function[t] = 1000
            sync_cost_function[t] = 0
        else:
            model_cost_function[t] = 1

    print(ali.factory.apply(log, net, marking, fmarking))


if __name__ == '__main__':
    execute_script()

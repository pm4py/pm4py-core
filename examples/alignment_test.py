import inspect
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
from pm4py.algo import alignments as ali
from pm4py.models import petri as petri
from pm4py import log as log_lib
from pm4py import util
from pm4py.log.importer.xes import factory as xes_importer


def align(trace, net, im, fm, model_cost_function, sync_cost_function):
    trace_costs = list(map(lambda e: 1000, trace))
    params = dict()
    params[util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = log_lib.util.xes.DEFAULT_NAME_KEY
    params[ali.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION] = model_cost_function
    params[ali.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION] = trace_costs
    params[ali.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    return ali.factory.apply(trace, net, im, fm, parameters=params, version=ali.factory.VERSION_STATE_EQUATION_A_STAR)


if __name__ == '__main__':
    log = xes_importer.import_log('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes')
    net, marking, fmarking = petri.importer.pnml.import_petri_from_pnml(
        'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32.pnml')

    model_cost_function = dict()
    sync_cost_function = dict()
    for t in net.transitions:
        if t.label is not None:
            model_cost_function[t] = 1000
            sync_cost_function[t] = 0
        else:
            model_cost_function[t] = 1

    print(list(map(lambda trace: align(trace, net, marking, fmarking, model_cost_function, sync_cost_function), log)))

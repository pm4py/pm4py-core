import inspect
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
import pm4py
from pm4py.algo.conformance import alignments as ali
from pm4py.entities import petri as petri
from pm4py.entities import log as log_lib
from pm4py import util
from pm4py.entities.log.importer.xes import factory as xes_importer


def align(trace, net, im, fm, model_cost_function, sync_cost_function):
    trace_costs = list(map(lambda e: 1000, trace))
    params = dict()
    params[util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = log_lib.util.xes.DEFAULT_NAME_KEY
    params[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION] = model_cost_function
    params[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION] = trace_costs
    params[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    return ali.factory.apply(trace, net, im, fm, parameters=params, version=ali.factory.VERSION_STATE_EQUATION_A_STAR)

def execute_script():
    log_path = os.path.join("..","tests","inputData","running-example.xes")
    pnml_path = os.path.join("..","tests","inputData","running-example.pnml")

    #log_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes'
    #pnml_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32.pnml'

    log = xes_importer.import_log(log_path)
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

    print(list(map(lambda trace: align(trace, net, marking, fmarking, model_cost_function, sync_cost_function), log)))

if __name__ == '__main__':
    execute_script()
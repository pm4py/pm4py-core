from pm4py.algo.conformance.tokenreplay import factory as tr_factory
from copy import copy


def compare_element_usage_two_logs(net, im, fm, log1, log2, parameters=None):
    if parameters is None:
        parameters = {}

    tr_parameters = copy(parameters)
    tr_parameters["enable_place_fitness"] = True

    rep_traces1, pl_fit_trace1, tr_fit_trace1, ne_act_model1 = tr_factory.apply(log1, net, im, fm,
                                                                                parameters=tr_parameters)
    rep_traces2, pl_fit_trace2, tr_fit_trace2, ne_act_model2 = tr_factory.apply(log2, net, im, fm,
                                                                                parameters=tr_parameters)

    print(pl_fit_trace1)


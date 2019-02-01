import os

from pm4py.algo.discovery.simple.model.log import factory as simple_extraction_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.stochastic_petri import map as stochastic_map
from pm4py.objects.stochastic_petri.lp_perf_bounds import LpPerfBounds
from pm4py.statistics.traces.log.case_arrival import get_case_arrival_avg
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.visualization.petrinet import factory as pn_vis_factory


def execute_script():
    log_name = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_name, variant="nonstandard")
    print("imported log")
    # obtain a simple, sound workflow net, containing only visibile unique transitions,
    # applying the Alpha Miner to some of the top variants (methods by Ale)
    activity_key = "concept:name"
    parameters = {PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key, PARAMETER_CONSTANT_ATTRIBUTE_KEY: activity_key}
    net, initial_marking, final_marking = simple_extraction_factory.apply(log, classic_output=True,
                                                                          parameters=parameters)
    print("obtained model")
    # visualize the output Petri net
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking)
    del gviz
    # pn_vis_factory.view(gviz)
    # gets the average time between cases starts
    avg_time_starts = get_case_arrival_avg(log)
    print("avg_time_starts real=", avg_time_starts)
    # gets the stochastic distribution associated to the Petri net and the log
    smap = stochastic_map.get_map_from_log_and_net(log, net, initial_marking, final_marking,
                                                   force_distribution="EXPONENTIAL")
    print("smap=", smap)

    perf_bound_obj = LpPerfBounds(net, initial_marking, final_marking, smap, avg_time_starts)
    net1, imarking1, fmarking1 = perf_bound_obj.get_net()
    gviz = pn_vis_factory.apply(net1, imarking1, fmarking1)

    for var in perf_bound_obj.var_corr:
        corr = perf_bound_obj.var_corr[var]

        minimum = perf_bound_obj.solve_problem(var, maximize=False)
        maximum = perf_bound_obj.solve_problem(var, maximize=True)

        print(var, minimum[corr], maximum[corr])


if __name__ == "__main__":
    execute_script()

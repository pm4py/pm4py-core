import os

from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet import factory as pn_vis_factory


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.import_log(log_path)
    print("loaded log")
    net, marking, final_marking = inductive_factory.apply(log)
    for place in marking:
        print("initial marking " + place.name)
    for place in final_marking:
        print("final marking " + place.name)
    gviz = pn_vis_factory.apply(net, marking, final_marking, parameters={"format": "svg"})
    pn_vis_factory.view(gviz)
    print("started token replay")
    aligned_traces = token_replay.apply(log, net, marking, final_marking)
    fit_traces = [x for x in aligned_traces if x['trace_is_fit']]
    perc_fitness = 0.00
    if len(aligned_traces) > 0:
        perc_fitness = len(fit_traces) / len(aligned_traces)
    print("perc_fitness=", perc_fitness)


if __name__ == "__main__":
    execute_script()

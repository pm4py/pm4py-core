import os

from pm4py.algo.conformance.tokenreplay import factory as token_based_replay
from pm4py.algo.conformance.tokenreplay.diagnostics import duration_diagnostics
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.filtering.tracelog import auto_filter as auto_filter
from pm4py.objects.log.importer.xes import factory as xes_importer


def execute_script():
    log = xes_importer.import_log(os.path.join("..", "tests", "input_data", "receipt.xes"))
    filtered_log = auto_filter.auto_filter.apply_auto_filter(log)
    net, initial_marking, final_marking = inductive_miner.apply(filtered_log)
    replayed_traces, place_fitness, trans_fitness, unwanted_activities = token_based_replay.apply(log, net,
                                                                                                  initial_marking,
                                                                                                  final_marking,
                                                                                                  parameters={
                                                                                                      "disable_variants": True,
                                                                                                      "enable_pltr_fitness": True})
    trans_diagnostics = duration_diagnostics.diagnose_from_trans_fitness(log, trans_fitness)
    act_diagnostics = duration_diagnostics.diagnose_from_notexisting_activities(log, unwanted_activities)
    for trans in trans_diagnostics:
        print(trans, trans_diagnostics[trans])
    for act in act_diagnostics:
        print(act, act_diagnostics[act])


if __name__ == "__main__":
    execute_script()

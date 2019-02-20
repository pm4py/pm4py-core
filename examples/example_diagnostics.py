import os

from pm4py.algo.conformance.tokenreplay import factory as token_based_replay
from pm4py.algo.conformance.tokenreplay.diagnostics import duration_diagnostics
from pm4py.algo.conformance.tokenreplay.diagnostics import root_cause_analysis
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.filtering.log import auto_filter as auto_filter
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

    # build decision trees
    string_attributes = ["org:group"]
    numeric_attributes = []

    parameters = {"string_attributes": string_attributes, "numeric_attributes": numeric_attributes}

    trans_root_cause = root_cause_analysis.diagnose_from_trans_fitness(log, trans_fitness, parameters=parameters)

    print("trans_root_cause=", trans_root_cause)

    for trans in trans_root_cause:
        clf = trans_root_cause[trans]["clf"]
        feature_names = trans_root_cause[trans]["feature_names"]
        classes = trans_root_cause[trans]["classes"]
        # visualization could be called
        # gviz = dt_vis_factory.apply(clf, feature_names, classes)
        # dt_vis_factory.view(gviz)

    act_root_cause = root_cause_analysis.diagnose_from_notexisting_activities(log, unwanted_activities,
                                                                              parameters=parameters)

    print("act_root_cause=", act_root_cause)

    for act in act_root_cause:
        clf = act_root_cause[act]["clf"]
        feature_names = act_root_cause[act]["feature_names"]
        classes = act_root_cause[act]["classes"]
        # visualization could be called
        # gviz = dt_vis_factory.apply(clf, feature_names, classes)
        # dt_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()

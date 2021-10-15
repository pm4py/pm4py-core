import os

import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.end_activities.log import get as end_activities_get
from pm4py.statistics.start_activities.log import get as start_activities_get

LOGS_FOLDER = "../compressed_input_data"
CLASSIFIER = "@@classifier"
ENABLE_ALIGNMENTS = False
NOISE_THRESHOLD = 0.5

for log_name in os.listdir(LOGS_FOLDER):
    if "xes" in log_name:
        log_path = os.path.join(LOGS_FOLDER, log_name)
        from pm4py.statistics.attributes.log import get as attributes_get_log

        log = pm4py.read_xes(log_path)
        for trace in log:
            for event in trace:
                if True and "lifecycle:transition" in event:
                    event["@@classifier"] = event["concept:name"] + "+" + event["lifecycle:transition"]
                    # event["concept:name"] = event["concept:name"] + "+" + event["lifecycle:transition"]
                else:
                    event["@@classifier"] = event["concept:name"]

        activities = attributes_get_log.get_attribute_values(log, CLASSIFIER)
        start_activities = start_activities_get.get_start_activities(log, parameters={
            "pm4py:param:activity_key": CLASSIFIER})
        end_activities = end_activities_get.get_end_activities(log, parameters={
            "pm4py:param:activity_key": CLASSIFIER})
        dfg = dfg_discovery.apply(log, parameters={
            "pm4py:param:activity_key": CLASSIFIER})
        fp_log = pm4py.algo.discovery.footprints.log.variants.entire_event_log.apply(log, parameters={
            "pm4py:param:activity_key": CLASSIFIER})

        tree_im_clean = inductive_miner.apply_tree_dfg(dfg, start_activities, end_activities, activities,
                                                       parameters={"noise_threshold": NOISE_THRESHOLD},
                                                       variant=inductive_miner.Variants.IM_CLEAN)
        fp_tree_clean = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_im_clean)
        fp_conf_im_clean = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_clean)
        fitness_im_clean = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_clean,
                                                                                        fp_conf_im_clean)
        precision_im_clean = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_clean)

        print(log_name, fitness_im_clean, precision_im_clean)

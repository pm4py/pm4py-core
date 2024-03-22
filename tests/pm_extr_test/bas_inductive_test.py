import os
import traceback

from pm4py.util import constants, pandas_utils

import time
import pm4py
from pm4py.algo.discovery.inductive import algorithm as im_clean
from pm4py.statistics.variants.log import get as variants_get

LOGS_FOLDER = "../compressed_input_data"
CLASSIFIER = "@@classifier"
ENABLE_ALIGNMENTS = True
NOISE_THRESHOLD = 0.2
VARIANT = im_clean.Variants.IM
ENABLE_MULTIPROCESSING = False


if __name__ == "__main__":
    for log_name in os.listdir(LOGS_FOLDER):
        if "xes" in log_name or "parquet" in log_name:
            try:
                log_path = os.path.join(LOGS_FOLDER, log_name)
                print("")
                print(log_path)
                if "xes" in log_name:
                    from pm4py.statistics.attributes.log import get as attributes_get_log

                    log = pm4py.read_xes(log_path, return_legacy_log_object=True)
                    for trace in log:
                        for event in trace:
                            if True and "lifecycle:transition" in event:
                                event["@@classifier"] = event["concept:name"] + "+" + event["lifecycle:transition"]
                                # event["concept:name"] = event["concept:name"] + "+" + event["lifecycle:transition"]
                            else:
                                event["@@classifier"] = event["concept:name"]
                    activities = set(attributes_get_log.get_attribute_values(log, CLASSIFIER).keys())
                    variants = variants_get.get_variants(log, parameters={"pm4py:param:activity_key": CLASSIFIER})
                    fp_log = pm4py.algo.discovery.footprints.log.variants.entire_event_log.apply(log, parameters={
                        "pm4py:param:activity_key": CLASSIFIER})
                elif "parquet" in log_name:
                    from pm4py.statistics.attributes.pandas import get as attributes_get_pandas

                    dataframe = pandas_utils.DATAFRAME.read_parquet(log_path)
                    activities = set(attributes_get_pandas.get_attribute_values(dataframe, CLASSIFIER).keys())
                    variants = pm4py.get_variants_as_tuples(dataframe)
                    variants = {",".join(x): y for x, y in variants.items()}
                    fp_log = pm4py.algo.discovery.footprints.log.variants.entire_dataframe.apply(dataframe)
                print("start tree_im_clean")
                tree_im_clean = im_clean.apply(log, variant=VARIANT, parameters={"pm4py:param:activity_key": CLASSIFIER,
                                                                     "noise_threshold": NOISE_THRESHOLD, "multiprocessing": ENABLE_MULTIPROCESSING})
                print(tree_im_clean)
                print("end tree_im_clean")

                fp_tree_clean = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_im_clean)

                if not activities.issubset(fp_tree_clean["activities"]):
                    print("ALERT! activities of the tree are less than the ones in the log!")
                    print(activities.difference(fp_tree_clean["activities"]))
                    time.sleep(5)

                fp_conf_im_clean = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_clean)
                fitness_im_clean = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_clean,
                                                                                                fp_conf_im_clean)

                if ENABLE_ALIGNMENTS:
                    from pm4py.algo.conformance.alignments.process_tree.variants import search_graph_pt

                    alignments_clean = search_graph_pt.apply(log, tree_im_clean, parameters={
                        search_graph_pt.Parameters.ACTIVITY_KEY: CLASSIFIER})
                    from pm4py.algo.evaluation.replay_fitness.variants import alignment_based

                    fitness_al_clean = alignment_based.evaluate(alignments_clean)["average_trace_fitness"]
                    if fitness_al_clean < fitness_im_clean:
                        print("ALERT", fitness_al_clean, fitness_im_clean)
                        time.sleep(5)
                        #input()
                    else:
                        print("OK ALIGNMENTS", fitness_al_clean)

                precision_im_clean = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_clean)
                print("IMCLEAN fp-fitness=%.3f fp-precision=%.3f" % (fitness_im_clean, precision_im_clean))
            except:
                traceback.print_exc()
                input()

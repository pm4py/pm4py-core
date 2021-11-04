import os
import traceback

import pandas as pd

import pm4py
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.inductive.variants.im_clean import algorithm as im_clean
from pm4py.objects.process_tree.utils import bottomup as bottomup_disc
from pm4py.statistics.variants.log import get as variants_get

LOGS_FOLDER = "../compressed_input_data"
CLASSIFIER = "@@classifier"
ENABLE_ALIGNMENTS = False
NOISE_THRESHOLD = 0.0

for log_name in os.listdir(LOGS_FOLDER):
    if "xes" in log_name or "parquet" in log_name:
        try:
            log_path = os.path.join(LOGS_FOLDER, log_name)
            print("")
            print(log_path)
            if "xes" in log_name:
                from pm4py.statistics.attributes.log import get as attributes_get_log

                log = pm4py.read_xes(log_path)
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

                dataframe = pd.read_parquet(log_path)
                activities = set(attributes_get_pandas.get_attribute_values(dataframe, CLASSIFIER).keys())
                variants = pm4py.get_variants_as_tuples(dataframe)
                variants = {",".join(x): y for x, y in variants.items()}
                fp_log = pm4py.algo.discovery.footprints.log.variants.entire_dataframe.apply(dataframe)
            print("start tree_im_clean")
            tree_im_clean = im_clean.apply_tree(log, parameters={"pm4py:param:activity_key": CLASSIFIER,
                                                                 "noise_threshold": NOISE_THRESHOLD})
            print("end tree_im_clean")
            tree_im = inductive_miner.apply_tree_variants(variants, variant=inductive_miner.Variants.IM,
                                                          parameters={"pm4py:param:activity_key": CLASSIFIER})
            print(tree_im_clean)
            print(tree_im)
            tree_imf = inductive_miner.apply_tree_variants(variants, variant=inductive_miner.Variants.IMf,
                                                           parameters={"pm4py:param:activity_key": CLASSIFIER,
                                                                       "noiseThreshold": NOISE_THRESHOLD})
            tree_imd = inductive_miner.apply_tree_variants(variants, variant=inductive_miner.Variants.IMd,
                                                           parameters={"pm4py:param:activity_key": CLASSIFIER})
            fp_tree_clean = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_im_clean)
            fp_tree_im = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_im)
            fp_tree_imf = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_imf)
            fp_tree_imd = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_imd)

            if not activities.issubset(fp_tree_clean["activities"]):
                print("ALERT! activities of the tree are less than the ones in the log!")
                print(activities.difference(fp_tree_clean["activities"]))
                print(activities.difference(fp_tree_im["activities"]))
                input()

            fp_conf_im_clean = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_clean)
            fp_conf_im = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_im)
            fp_conf_imf = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_imf)
            fp_conf_imd = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_imd)
            fitness_im_clean = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_im,
                                                                                            fp_conf_im_clean)
            fitness_im = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_im, fp_conf_im)
            fitness_imd = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_imd, fp_conf_imd)
            fitness_imf = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_imf, fp_conf_imf)

            if ENABLE_ALIGNMENTS:
                from pm4py.algo.conformance.tree_alignments.variants import search_graph_pt

                alignments_clean = search_graph_pt.apply(log, tree_im_clean, parameters={
                    search_graph_pt.Parameters.ACTIVITY_KEY: CLASSIFIER})
                from pm4py.evaluation.replay_fitness.variants import alignment_based

                fitness_al_clean = alignment_based.evaluate(alignments_clean)["average_trace_fitness"]
                if fitness_al_clean < fitness_im_clean:
                    print("ALERT")
                    input()
                else:
                    print("OK ALIGNMENTS", fitness_al_clean)

            precision_im_clean = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_clean)
            precision_im = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_im)
            precision_imf = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_imf)
            precision_imd = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_imd)
            print("IMCLEAN fp-fitness=%.3f fp-precision=%.3f" % (fitness_im_clean, precision_im_clean))
            print("IM fp-fitness=%.3f fp-precision=%.3f" % (fitness_im, precision_im))
            print("IMf fp-fitness=%.3f fp-precision=%.3f" % (fitness_imf, precision_imf))
            print("IMd fp-fitness=%.3f fp-precision=%.3f" % (fitness_imd, precision_imd))
        except:
            bottomup_nodes = bottomup_disc.get_bottomup_nodes(tree_im_clean)
            for node in bottomup_nodes:
                if node.parent is None:
                    print(node, node.parent)
            traceback.print_exc()
            input()

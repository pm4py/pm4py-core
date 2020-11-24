import os

import pm4py
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import pandas as pd

LOGS_FOLDER = "../compressed_input_data"

for log_name in os.listdir(LOGS_FOLDER):
    if "xes" in log_name or "parquet" in log_name:
        log_path = os.path.join(LOGS_FOLDER, log_name)
        print("")
        print(log_path)
        if "xes" in log_name:
            log = pm4py.read_xes(log_path)
            variants = pm4py.get_variants(log)
            fp_log = pm4py.algo.discovery.footprints.log.variants.entire_event_log.apply(log)
        elif "parquet" in log_name:
            dataframe = pd.read_parquet(log_path)
            variants = pm4py.get_variants(dataframe)
            fp_log = pm4py.algo.discovery.footprints.log.variants.entire_dataframe.apply(dataframe)
        tree_im = inductive_miner.apply_tree_variants(variants, variant=inductive_miner.Variants.IM)
        tree_imf = inductive_miner.apply_tree_variants(variants, variant=inductive_miner.Variants.IMf)
        tree_imd = inductive_miner.apply_tree_variants(variants, variant=inductive_miner.Variants.IMd)
        fp_tree_im = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_im)
        fp_tree_imf = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_imf)
        fp_tree_imd = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree_imd)
        fp_conf_im = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_im)
        fp_conf_imf = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_imf)
        fp_conf_imd = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree_imd)
        fitness_im = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_im, fp_conf_im)
        fitness_imd = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_imd, fp_conf_imd)
        fitness_imf = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree_imf, fp_conf_imf)
        precision_im = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_im)
        precision_imf = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_imf)
        precision_imd = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree_imd)
        print("IM fp-fitness=%.3f fp-precision=%.3f" % (fitness_im, precision_im))
        print("IMf fp-fitness=%.3f fp-precision=%.3f" % (fitness_imf, precision_imf))
        print("IMd fp-fitness=%.3f fp-precision=%.3f" % (fitness_imd, precision_imd))

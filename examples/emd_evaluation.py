from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.evaluation.earth_mover_distance import algorithm as earth_mover_distance
from pm4py.statistics.variants.log import get as variants_get
from pm4py.algo.simulation.playout.petri_net import algorithm
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
import os


def execute_script():
    M = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01, ("a", "d", "c", "e"): 0.01}

    L1 = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
          ("a", "d", "c", "e"): 0.01}
    # the distance between M and L1, that we expect to be zero, is zero according to the EMD
    emd = earth_mover_distance.apply(M, L1)
    print("M L1 emd distance:", emd)

    L2 = {("a", "b", "e"): 0.5, ("a", "b", "d", "e"): 0.245, ("a", "d", "b", "e"): 0.245, ("a", "c", "d", "e"): 0.005,
          ("a", "d", "c", "e"): 0.005}
    # the distance between M and L2 according to the EMD is 0.1275 (paper value 0.125)
    emd = earth_mover_distance.apply(M, L2)
    print("M L2 emd distance:", emd)

    L3 = {("a", "b", "d", "e"): 0.489, ("a", "d", "b", "e"): 0.489, ("a", "c", "d", "e"): 0.01,
          ("a", "d", "c", "e"): 0.01, ("a", "b", "e"): 0.002}
    # the distance between M and L3 according to the EMD is 0.0005 (paper value 0.0005), perfect!
    emd = earth_mover_distance.apply(M, L3)
    print("M L3 emd distance:", emd)

    L4 = {("a", "b", "d", "e"): 0.5, ("a", "d", "b", "e"): 0.5}
    # the distance between M and L4 according to the EMD is 0.005 (paper value 0.005), perfect!
    emd = earth_mover_distance.apply(M, L4)
    print("M L4 emd distance:", emd)

    L5 = {("a", "c", "d", "e"): 0.5, ("a", "d", "c", "e"): 0.5}
    # the distance between M and L5 according to the EMD is 0.245 (paper value 0.245), perfect!
    emd = earth_mover_distance.apply(M, L5)
    print("M L5 emd distance:", emd)

    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    lang_log = variants_get.get_language(log)
    net0, im0, fm0 = alpha_miner.apply(log)
    process_tree = inductive_miner.apply(log)
    net1, im1, fm1 = process_tree_converter.apply(process_tree)
    lang_model0 = variants_get.get_language(
        algorithm.apply(net0, im0, fm0, variant=algorithm.Variants.STOCHASTIC_PLAYOUT,
                        parameters={algorithm.Variants.STOCHASTIC_PLAYOUT.value.Parameters.LOG: log}))
    lang_model1 = variants_get.get_language(
        algorithm.apply(net1, im1, fm1, variant=algorithm.Variants.STOCHASTIC_PLAYOUT,
                        parameters={algorithm.Variants.STOCHASTIC_PLAYOUT.value.Parameters.LOG: log}))
    emd = earth_mover_distance.apply(lang_model0, lang_log)
    print("running-example alpha emd distance: ", emd)
    emd = earth_mover_distance.apply(lang_model1, lang_log)
    print("running-example inductive emd distance: ", emd)

    #log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    #net, im, fm = inductive_miner.apply(log)
    #lang_model = variants_get.get_language(simulator.apply(net, im, fm, variant=simulator.Variants.STOCHASTIC_PLAYOUT,
    #                                                       parameters={
    #                                                           simulator.Variants.STOCHASTIC_PLAYOUT.value.Parameters.LOG: log}))
    #emd = earth_mover_distance.apply(lang_model, lang_log)
    #print("receipt inductive emd distance: ", emd)


if __name__ == "__main__":
    execute_script()

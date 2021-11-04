import os
from pm4py.algo.conformance.multialignments.variants.discounted_a_star import apply as multii
from pm4py.algo.conformance.multialignments.algorithm import Parameters
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer


if __name__ == '__main__':
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    THETA = 1.1
    MU =  20
    multiali = multii(log,net,marking,fmarking, parameters={Parameters.EXPONENT:THETA, Parameters.MARKING_LIMIT:MU})
    print("Multi-alignment:",multiali['multi-alignment'])
    print("Maximal Levenshtein Edit Distance to Log:", multiali['max_distance_to_log'])

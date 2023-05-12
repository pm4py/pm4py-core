import os

from pm4py.algo.conformance.antialignments.variants.discounted_a_star import apply as antii
from pm4py.algo.conformance.antialignments.algorithm import Parameters
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer


if __name__ == '__main__':
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    THETA = 1.5
    MU =  20
    EPSILON = 0.01
    resAnti = antii(log,net,marking,fmarking, parameters={Parameters.EXPONENT:THETA,
                                                          Parameters.EPSILON:EPSILON,
                                                          Parameters.MARKING_LIMIT:MU})
    print(resAnti['anti-alignment'])
    print("Precision:",resAnti['precision'])


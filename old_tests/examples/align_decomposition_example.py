from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.conformance.decomp_alignments import factory as dec_align_factory
from pm4py.evaluation.replay_fitness import factory as rep_fit_factory
import os


def execute_script():
    # import the a32f0n00 log
    log = xes_importer.apply(os.path.join("..", "tests", "compressed_input_data", "09_a32f0n00.xes.gz"))
    # discover a model using the inductive miner
    net, im, fm = inductive_miner.apply(log)
    # apply the alignments decomposition with a maximal number of border disagreements set to 5
    aligned_traces = dec_align_factory.apply(log, net, im, fm, parameters={"thresh_border_agreement": 5})
    #print(aligned_traces)
    # calculate the fitness over the recomposed alignment (use the classical evaluation factory)
    fitness = rep_fit_factory.evaluate(aligned_traces, variant="alignments")
    print(fitness)

if __name__ == "__main__":
    execute_script()

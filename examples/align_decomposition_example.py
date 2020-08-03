try:
    import pm4pycvxopt
except:
    pass

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.conformance.decomp_alignments import algorithm as dec_align
from pm4py.evaluation.replay_fitness import evaluator as rep_fit
import os


def execute_script():
    # import the a32f0n00 log
    log = xes_importer.apply(os.path.join("..", "tests", "compressed_input_data", "09_a32f0n00.xes.gz"))
    # discover a model using the inductive miner
    net, im, fm = inductive_miner.apply(log)
    # apply the alignments decomposition with a maximal number of border disagreements set to 5
    aligned_traces = dec_align.apply(log, net, im, fm, parameters={
        dec_align.Variants.RECOMPOS_MAXIMAL.value.Parameters.PARAM_THRESHOLD_BORDER_AGREEMENT: 5})
    # print(aligned_traces)
    # calculate the fitness over the recomposed alignment (use the classical evaluation)
    fitness = rep_fit.evaluate(aligned_traces, variant=rep_fit.Variants.ALIGNMENT_BASED)
    print(fitness)


if __name__ == "__main__":
    execute_script()

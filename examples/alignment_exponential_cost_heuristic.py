import os
import time
from pm4py.algo.conformance.alignments import algorithm as ali
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri.importer import importer as petri_importer
from pm4py.statistics.variants.log.get import get_variants
import numpy as np
from tqdm.auto import tqdm

'''
This file aims at experimenting all the version of alignments for a paper which is under submission.
Author: Boltenhagen Mathilde
Date: Nov. 2020
'''


def moves_and_runtimes_alignment(log_path, pnml_path, version, parameters):
    '''
    This function has been used to compute the differences, in term of log+model moves, between alignements
    @log_path (string): path of the log file
    @pnml_path (string): path of the model file (Petri net)
    @version: given in pm4py.algo.conformance.alignments
    @:parameter: parameter of the version
    :return: mean(number of moves),std(number of moves), sum(runtime)
    '''

    net, marking, fmarking = petri_importer.apply(pnml_path)
    log = xes_importer.apply(log_path)


    #uncomment to visualize from pm4py.visualization.petrinet.visualizer import apply as vizu
    #vizu(net, marking,fmarking).view()

    # firt we get the variants:
    variants = get_variants(log)

    # we save asyn moves, time and length of variants
    sum_asyn_moves=[]
    diff_time=[]
    lent=[]

    for i in tqdm(variants):
        trace = variants[i][0]
        lent.append(len(trace))

        start = time.time()
        alignments = ali.apply(trace, net, marking, fmarking,variant=version, parameters=parameters)
        #print(alignments)

        # save time to run this alignment
        end = time.time()
        diff_time.append((end-start))

        # get the number of moves
        moves = (len(str(alignments["alignment"]).split(">>")))-1
        sum_asyn_moves.append(moves)

    return str("{:.2f}".format(sum(sum_asyn_moves) / len(sum_asyn_moves))+"\t"+ "{:.2f}".format(np.std(sum_asyn_moves))+ "\t"+"{:.2f}".format(sum(diff_time)))


def run_experiments(log_path,pnml_path):
    '''
    Runs the different versions that exist in pm4py
    '''

    print("VERSION_DIJKSTRA_NO_HEURISTICS\t", moves_and_runtimes_alignment(log_path,pnml_path, ali.VERSION_DIJKSTRA_NO_HEURISTICS,{}))
    print("VERSION_DIJKSTRA_LESS_MEMORY\t",moves_and_runtimes_alignment(log_path,pnml_path,ali.VERSION_DIJKSTRA_LESS_MEMORY,{}))
    print("DEFAULT_VARIANT\t",moves_and_runtimes_alignment(log_path,pnml_path,ali.DEFAULT_VARIANT,{}))
    print("VERSION_STATE_EQUATION_A_STAR\t",moves_and_runtimes_alignment(log_path,pnml_path,ali.VERSION_STATE_EQUATION_A_STAR,{}))

    # run different base of logarithm
    for i in [2, 1, 1.25, 1.5, 1.75, 2]:
        parameters = {ali.Parameters.SYNCHRONOUS:True, ali.Parameters.EXPONENT:i}
        print("VERSION_EXPONENTIAL_COST_HEURISTIC Petri Only",str(i),"\t",moves_and_runtimes_alignment(log_path,pnml_path,ali.VERSION_EXPONENTIAL_COST_HEURISTIC, parameters))

        parameters = {ali.Parameters.SYNCHRONOUS:False, ali.Parameters.EXPONENT:i}
        print("VERSION_EXPONENTIAL_COST_HEURISTIC SynchProduct",str(i),"\t",moves_and_runtimes_alignment(log_path,pnml_path,ali.VERSION_EXPONENTIAL_COST_HEURISTIC, parameters))


if __name__ == '__main__':
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    run_experiments(log_path,pnml_path)
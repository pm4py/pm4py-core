import os
import time
from pm4py.algo.conformance.alignments import algorithm as ali
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri.importer import importer as petri_importer


def testSynchronousDiscountedAlignment():
    '''
    This function runs an alignment based on the exponential cost function
    By using the synchronous product
    :return:
    '''
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    # to see the net :
    #vizu(net,marking,fmarking).view()

    start=time.time()

    alignments1 = ali.apply(log, net, marking, fmarking,
                            variant=ali.VERSION_DISCOUNTED_A_STAR,
                            parameters={ali.Parameters.SYNCHRONOUS:True,ali.Parameters.EXPONENT:1.1})
    print(alignments1)
    print("Time:",(time.time()-start))

def testNoSynchronousDiscountedAlignment():
    '''
    This function runs an alignment based on the exponential cost function
    By using the Petri net and exponentialCost function
    :return:
    '''
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    start=time.time()

    alignments1 = ali.apply(log._list[0], net, marking, fmarking,
                            variant=ali.VERSION_DISCOUNTED_A_STAR,
                            parameters={ali.Parameters.SYNCHRONOUS:False,ali.Parameters.EXPONENT:1.1})
    print(alignments1)
    print("Time:",(time.time()-start))


if __name__ == '__main__':
    testSynchronousDiscountedAlignment()
    # currently plays only the first trace
    testNoSynchronousDiscountedAlignment()
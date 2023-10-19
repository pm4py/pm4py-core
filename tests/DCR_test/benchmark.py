import pm4py
import pandas as pd
from matplotlib import pyplot as plt
import math
import time
import numpy as np
from pm4py.discovery import discover_dcr, discover_declare
def benchmark_discover():
    # import algorithm


    # how much should it be repeated
    repeat = 10

    # initiate structure needed to provide information
    times = []
    no_event = []
    no_of_act = []

    # loop to import all algorithm
    for i in range(1, 11):
        result = []
        # import training log
        training_log = pm4py.read_xes('../../tests/input_data/pdc/pdc_2019/Training Logs/pdc_2019_' + str(i) + '.xes')
        dcr = None
        # pm4py needs a timestamp, so a assign random values
        add = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        training_log['time:timestamp'] = add
        # nested loop for running the discover the repeated times
        for j in range(repeat):
            # use time to get internal counter
            start_time = time.perf_counter()

            # perform discovery
            dcr, la = discover_dcr(training_log)

            # get the difference
            end_time = time.perf_counter() - start_time
            # append the result
            result.append(end_time)

        print("result from test: " + str(i) + ": " + str((sum(result) / repeat) * 1000) + " ms")
        print("length of event log: " + str(len(training_log)))
        #print("number of actitivies: " + str(len(set(training_log['concept:name']))))
        times.append((sum(result) / repeat) * 1000)
        no_event.append(len(training_log))
        no_of_act.append(len(set(training_log['concept:name'])))


    x = [i for i in range(1, 11)]
    y = times
    plt.plot(x, y)
    plt.title("DisCoveR miner for PM4Py")
    plt.ylabel('run time in ms')
    plt.xlabel('pdc logs 1 to 10')
    plt.grid(axis='x')
    plt.grid(axis='y')
    plt.show()


def test_ground_truth_compliance():
    prec = []
    recall = []
    acc = []
    pred = []
    for i in range(1,11):
        training_log = pm4py.read_xes('../../tests/input_data/pdc/pdc_2019/Training Logs/pdc_2019_'+str(i)+'.xes')
        # pm4py needs a timestamp, so a assign random values
        add = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        training_log['time:timestamp'] = add

        dcr, la = discover_dcr(training_log)


        #import graph for ground truth
        gt_log = pm4py.read_xes('../../tests/input_data/pdc/pdc_2019/Ground Truth Logs/pdc_2019_'+str(i)+'.xes')
        # pm4py needs a timestamp, so a assign random values
        add = pd.date_range('2018-04-09', periods=len(gt_log), freq='20min')
        gt_log['time:timestamp'] = add
        gt_log = pm4py.convert_to_event_log(gt_log)
        from pm4py.algo.evaluation.compliance.variants.confusion_matrix import compliancechecker
        com = compliancechecker()
        res = com.compliant_traces(dcr,gt_log)
        prec.append(res.computePrecision())
        recall.append(res.computeRecall())
        acc.append(res.computeAccuracy())
        pred.append(res.get_f_score())

    total_true_neg = 0
    total_true_pos = 0
    total_false_pos =  0
    total_false_neg = 0

    for i in pred:
        values = list(i)
        total_true_neg += values[2]
        total_true_pos += values[0]
        total_false_pos += values[1]
        total_false_neg += values[3]

    #compute the precision according to positive and negative traces
    neg_prec = total_true_neg / (total_true_neg + total_false_neg)
    pos_prec = total_true_pos / (total_true_pos + total_false_pos)
    neg_recall = total_true_neg / (total_true_neg + total_false_pos)
    pos_recall = total_true_pos / (total_true_pos + total_false_neg)

    #calculate the harmanic mean of precision and recall
    weight = 1
    f1_positive_score = ((1 + weight) * pos_prec * pos_recall) / (weight * pos_prec + pos_recall)
    f1_negative_score = ((1 + weight) * neg_prec * neg_recall) / (weight * neg_prec + neg_recall)
    acc = (total_true_pos + total_true_neg) / (total_true_pos + total_true_neg + total_false_pos + total_false_neg)

    # It measures the differences between actual values and predicted values
    # and is equivalent to the chi-square statistic for a 2 x 2 contingency table
    numerator = (total_true_neg * total_true_pos) - (total_false_neg * total_false_pos)
    Denominator = (total_true_pos + total_false_pos)*(total_true_pos + total_false_neg)*(total_true_neg + total_false_pos)*(total_true_neg + total_false_neg)
    mcc = numerator / math.sqrt(Denominator)

    print("positive precision: "+str(round(pos_prec,2)))
    print("negative precision: "+str(round(neg_prec,2)))
    print("positive recall: " + str(round(pos_recall,2)))
    print("negative recall: "+str(round(neg_recall,2)))
    print("positive f_1 score: "+str(round(f1_positive_score,2)))
    print("negative f_1 score: " + str(round(f1_negative_score,2)))
    print("accuracy: "+str(round(acc*100,1)))
    print("mcc: "+str(round(mcc,2)))
    #print("observed results"+str(observed))
    #print("mean acc: "+str(mean_prec))



if __name__ == "__main__":
    #comment out what you want to test the benchmark for
    #test_ground_truth_compliance()
    benchmark_discover()
    pass

import os
from pm4py.objects.log.importer.xes import importer

import numpy as np
import os
import pm4py
import csv
from math import sqrt
from copy import deepcopy
from pm4py.objects.log.importer.xes import importer
from pm4py.objects.log.obj import EventLog
from pm4py.objects.dcr import semantics as dcr_semantics

minerPath = "./DisCoveR.jar"
testDir = "../logs/PDC2020/TestLogs/"
truthDir = "../logs/PDC2020/GroundTruthLogs/"
classifiedDir = "../__generated/classified-logs/"
modelDir = "../__generated/models/"
exportPath = "../results/results-fuzzy-abs"

def fitness(event_log, dcr_model, cmd_print=False):
    no_traces = len(event_log)
    no_accepting = 0
    for trace in event_log:
        trace_to_print = []
        can_execute = True
        dcr = deepcopy(dcr_model)
        semantics = dcr_semantics.DcrSemantics(dcr, cmd_print=False)
        for event in trace:
            (executed, _) = semantics.execute(event['concept:name'])
            trace_to_print.append(event['concept:name'])
            if executed is False:
                can_execute = False
                break
        accepting = semantics.is_accepting()
        if can_execute and accepting:
            no_accepting = no_accepting + 1
        else:
            print(f'[x] Failing trace: {trace_to_print}') if cmd_print else None
    return no_accepting, no_traces

def confusion_matrix_from_dcr(dcr, test_log, truthLog):
    # log = list(importer.apply(classifiedDir + filename))
    log = test_log
    # truthLog = importer.apply(truthDir + filename)
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    log.sort(key=(lambda x: int(x.attributes["concept:name"])))
    log = EventLog(log)
    for i, trace in enumerate(log):
        trace = log[i].attributes
        truthTrace = truthLog[i].attributes
        if str(trace["concept:name"]) != str(truthTrace["concept:name"]):
            # print(filename)
            print(trace["concept:name"])
            print(truthTrace["concept:name"])
            raise Exception("Trace ID mismatch! Aborting.")
        traceIsPos = trace["pdc:isPos"]
        truthTraceIsPos = truthTrace["pdc:isPos"] == "True"
        if traceIsPos:
            if truthTraceIsPos:
                tp += 1
            else:
                fp += 1
        else:
            if truthTraceIsPos:
                fn += 1
            else:
                tn += 1
    print(f'tp: {tp}| fp: {fp} | tn: {tn} | fn: {fn}')
    return tp, fp, tn, fn
def confusion_matrix(log, truthLog):
    # log = list(importer.apply(classifiedDir + filename))
    # truthLog = importer.apply(truthDir + filename)
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    log.sort(key=(lambda x: int(x.attributes["concept:name"])))
    log = EventLog(log)
    for i, trace in enumerate(log):
        trace = log[i].attributes
        truthTrace = truthLog[i].attributes
        if str(trace["concept:name"]) != str(truthTrace["concept:name"]):
            # print(filename)
            print(trace["concept:name"])
            print(truthTrace["concept:name"])
            raise Exception("Trace ID mismatch! Aborting.")
        traceIsPos = trace["pdc:isPos"]
        truthTraceIsPos = truthTrace["pdc:isPos"] == "True"
        if traceIsPos:
            if truthTraceIsPos:
                tp += 1
            else:
                fp += 1
        else:
            if truthTraceIsPos:
                fn += 1
            else:
                tn += 1
    print(f'tp: {tp}| fp: {fp} | tn: {tn} | fn: {fn}')
    return tp, fp, tn, fn

def confusionMatrix(trainingDir, genDir, root, exportPath, showPrint=False):

    minerPath = root + "DisCoveR.jar"
    testDir = root + "DataSet/PDC2019/test-logs/"
    truthDir = root + "DataSet/PDC2019/ground-truth-logs/"

    classifiedDir = genDir + "classifiedLogs/"
    modelDir = genDir + "models/"

    # Ensure folders exists
    if not os.path.isdir(classifiedDir):
        os.mkdir(classifiedDir)
    if not os.path.isdir(modelDir):
        os.mkdir(modelDir)

    # Generate models from trainingDir
    for filename in os.listdir(trainingDir):
        if filename.endswith(".xes"):
            cmd = "java -jar " + minerPath + " -PDC " + trainingDir + filename + " " + modelDir + filename[:-4]
            stream = os.popen(cmd)
            print(stream.read()) if showPrint else None

    # Classify testDir based on model
    for filename in os.listdir(modelDir):
        cmd = "java -jar " + minerPath + " -classifyPDC " + testDir + filename + ".xes " + modelDir + filename + " " + classifiedDir + filename + ".xes true"
        # print(cmd)
        stream = os.popen(cmd)
        print(stream.read()) if showPrint else None

    f = open(exportPath, "w")
    header = "log_name;tp;fp;tn;fn\n"
    f.write(header)

    for filename in os.listdir(classifiedDir):
        if filename.endswith(".xes"):
            log = list(importer.apply(classifiedDir + filename))
            truthLog = importer.apply(truthDir + filename)
            tp = 0
            fp = 0
            tn = 0
            fn = 0
            log.sort(key=(lambda x: int(x.attributes["concept:name"])))
            log = EventLog(log)
            for i, trace in enumerate(log):
                trace = log[i].attributes
                truthTrace = truthLog[i].attributes
                if str(trace["concept:name"]) != str(truthTrace["concept:name"]):
                    print(filename)
                    print(trace["concept:name"])
                    print(truthTrace["concept:name"])
                    raise Exception("Trace ID mismatch! Aborting.")
                traceIsPos = trace["pdc:isPos"]
                truthTraceIsPos = truthTrace["pdc:isPos"] == "True"
                if traceIsPos:
                    if truthTraceIsPos:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if truthTraceIsPos:
                        fn += 1
                    else:
                        tn += 1
        line = filename + ";" + str(tp) + ";" + str(fp) + ";" + str(tn) + ";" + str(fn) + "\n"
        f.write(line)
    f.close()


def pdcFscore(tp, fp, tn, fn):
    try:
        posAcc = tp / (tp + fn)
        negAcc = tn / (tn + fp)
        res = 2 * posAcc * negAcc / (posAcc + negAcc)
        return res
    except:
        return 0


def fscore(tp, fp, tn, fn):
    try:
        recall = tp / (tp + fn)
        prec = tp / (tp + fp)
        res = 2 * recall * prec / (recall + prec)
        return res
    except:
        return 0


def balancedAccuracy(tp, fp, tn, fn):
    try:
        posAcc = tp / (tp + fn)
        negAcc = tn / (tn + fp)
        res = (posAcc + negAcc) / 2
        return res
    except:
        return 0


def mcc(tp, fp, tn, fn):
    try:
        num = tp * tn - fp * fn
        tmp = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        denom = sqrt(tmp)
        res = num / denom
        return res
    except:
        return 0

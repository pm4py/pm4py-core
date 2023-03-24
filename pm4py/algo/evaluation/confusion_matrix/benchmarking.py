import numpy as np
import os
import csv
from math import sqrt
from pm4py.objects.log.importer.xes import importer
from pm4py.objects.log.obj import EventLog

def confusionMatrix(trainingDir, genDir, root, exportPath, showPrint=False):
    def _print(str):
        if showPrint:
            print(str)

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
            _print(stream.read())
    
    # Classify testDir based on model
    for filename in os.listdir(modelDir):
        cmd = "java -jar " + minerPath + " -classifyPDC " + testDir + filename + ".xes " + modelDir + filename + " " + classifiedDir + filename + ".xes true"
        #print(cmd)
        stream = os.popen(cmd)
        _print(stream.read())

    f = open(exportPath, "w")
    header = "log_name;tp;fp;tn;fn\n"
    f.write(header)

    for filename in os.listdir(classifiedDir):
        if filename.endswith(".xes"):
            log = list(importer.apply(classifiedDir+filename))
            truthLog = importer.apply(truthDir+filename)
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
        res    = 2 * posAcc * negAcc / (posAcc + negAcc)
        return res
    except:
        return 0

def fscore(tp, fp, tn, fn):
    try:
        recall = tp / (tp + fn)
        prec   = tp / (tp + fp)
        res    = 2 * recall * prec / (recall + prec)
        return res
    except:
        return 0

def balancedAccuracy(tp, fp, tn, fn):
    try:
        posAcc = tp / (tp + fn)
        negAcc = tn / (tn + fp)
        res    = (posAcc + negAcc) / 2 
        return res
    except:
        return 0

def mcc(tp, fp, tn, fn):
    try:
        num   = tp * tn - fp * fn
        tmp   = (tp + fp)*(tp + fn)*(tn + fp)*(tn + fn)
        denom = sqrt(tmp)
        res   = num / denom
        return res
    except:
        return 0

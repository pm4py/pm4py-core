import pandas

import pm4py
import numpy as np
from pm4py.objects.dcr.semantics import DCRSemantics
from copy import deepcopy
from typing import Tuple
from pm4py.objects.log.obj import EventLog

class complianceResult:
    '''
    class to store the collection of result from compliance

    contains function to compute the value for the confusion matrix
    '''
    def __init__(self):
        self.truePositive = 0
        self.falsePositive = 0
        self.trueNegative = 0
        self.falseNegative = 0

    def addTraceResult(self,expectedResult,actualResult):
        '''
        this function notes, if a trace is true positive/negative or false positive/negative
        based on ground truth log expected result and the actually result

        Parameters
        ----------
        :param expectedResult: expected result of trace
        :param actualResult: actual result of trace

        Returns
        -------
        '''
        if actualResult == True:
            if expectedResult == True:
                self.truePositive += 1
            else:
                self.falsePositive += 1
        else:
            if expectedResult == True:
                self.falseNegative += 1
            else:
                self.trueNegative += 1

    def computeAccuracy(self) -> float:
        #returns how accurate the model is according to expected behavior:
        #acc. = (TP+TN)/(TP+TN+FP+FN)
        return (self.truePositive+self.trueNegative)/(self.trueNegative+self.truePositive+self.falseNegative+self.falsePositive)

    def computePrecision(self) -> float:
        # prec. = (TP)/(TP+FP)
        #returns value of how precise the model reflect the expected behavior
        return (self.truePositive)/(self.truePositive+self.falsePositive)

    def computeRecall(self) -> float:
        #recall = (TP)/(TP+FN)
        #return value of how well the model has captured expected behavior
        return (self.truePositive)/(self.falseNegative+self.truePositive)

    def get_f_score(self) -> Tuple[int, int, int, int]:
        return self.truePositive,self.falsePositive,self.trueNegative,self.falseNegative


class ComplianceChecker:
    """
    The compliance checker, will take in, a dcr graph and a ground truth log

    this implementation is based on the compliance checker for DisCoveR java implementation used to analyze:
    - accuracy
    - precision
    - recall/fitness

    runs traces extracted from a ground truth log
    use function from dcrsemantics run, returns none if the trace is deviating
    if trace is deviating from model return false

    if trace can be executed return dcr graph and marking, check if the graph is accepting
    """
    def apply(self, graph, gt_log):
        compliance_res = self.compliant_traces(graph, gt_log)
        precision = compliance_res.computePrecision()
        accuracy = compliance_res.computeAccuracy()
        recall = compliance_res.computeRecall()
        return (precision, accuracy, recall, compliance_res.truePositive, compliance_res.falsePositive,
                compliance_res.trueNegative, compliance_res.falseNegative)

    def compliant_traces(self, graph, gt_log):
        #Eventlog and pandas dataframe requires two different approaches
        compliance_res = complianceResult()
        sem = DCRSemantics()
        initial_marking = deepcopy(graph.marking)
        for trace in gt_log:
            actual_value = True
            for e in trace:
                if not sem.is_enabled(e['concept:name'], graph):
                    actual_value = False
                else:
                    graph = sem.execute(graph, e['concept:name'])
            graph.marking.reset(deepcopy(initial_marking))
            if not sem.is_accepting(graph):
                compliance_res.addTraceResult(trace.attributes['pdc:isPos'], False)
            else:
                compliance_res.addTraceResult(trace.attributes['pdc:isPos'], actual_value)
        return compliance_res


                

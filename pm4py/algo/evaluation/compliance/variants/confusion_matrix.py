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
        self.__truePositive = 0
        self.__falsePositive = 0
        self.__trueNegative = 0
        self.__falseNegative = 0

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
                self.__truePositive += 1
            else:
                self.__falsePositive += 1
        else:
            if expectedResult == True:
                self.__falseNegative += 1
            else:
                self.__trueNegative += 1

    def computeAccuracy(self) -> float:
        #returns how accurate the model is according to expected behavior:
        #acc. = (TP+TN)/(TP+TN+FP+FN)
        return (self.__truePositive+self.__trueNegative)/(self.__trueNegative+self.__truePositive+self.__falseNegative+self.__falsePositive)

    def computePrecision(self) -> float:
        # prec. = (TP)/(TP+FP)
        #returns value of how precise the model reflect the expected behavior
        return (self.__truePositive)/(self.__truePositive+self.__falsePositive)

    def computeRecall(self) -> float:
        #recall = (TP)/(TP+FN)
        #return value of how well the model has captured expected behavior
        return (self.__truePositive)/(self.__falseNegative+self.__truePositive)

    def get_f_score(self) -> Tuple[int, int, int, int]:
        return self.__truePositive,self.__falsePositive,self.__trueNegative,self.__falseNegative


class compliancechecker:
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

    def compliant_traces(self,dcr,gt_log, parameters=None):
        #Eventlog and pandas dataframe requires two different approaches
        compliance_res = complianceResult()
        for trace in gt_log:
            sem = DCRSemantics
            res = sem.run(deepcopy(dcr), trace)
            if res is None:
                compliance_res.addTraceResult(trace.attributes['pdc:isPos'], False)
            else:
                actualResult = sem.is_accepting(res)
                compliance_res.addTraceResult(trace.attributes['pdc:isPos'], actualResult)
        return compliance_res


                

import os
import unittest

import pandas
import pandas as pd
import pm4py
import matplotlib as plt

class Test_conformance_dcr(unittest.TestCase):
    def test_rule_checking_conformance(self):
        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # when process is discovered, should be perfect fitting to traces:
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        dcr, la = pm4py.discover_dcr(log)
        # then the models should have perfect fitness
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # change assertion, it should check for each trace and its fitness
        res = conf_alg(log, dcr)

        # this has been implemented as it allows us to check the shape of the template more accurately
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'],True)


    def test_rule_checking_dataframe(self):
        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # when process is discovered, should be perfect fitting to traces:
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        dcr, la = apply(log)

        # then the models should have perfect fitness
        from pm4py.conformance import conformance_dcr
        res = conformance_dcr(log,dcr,return_diagnostics_dataframe=True)
        # change assertion, it should check for each trace and its fitness
        # this has been implemented as it allows us to check the shape of the template more accurately
        self.assertIsInstance(res,pandas.DataFrame)

    def test_conformance_with_resource_as_roles(self):
        # For testing deviations, we needed two different logs for the same process
        # used a pdc log
        #given a training log and test log
        log = pm4py.read_xes('../input_data/roadtraffic100traces.xes')
        log = log.groupby("case:concept:name").apply(lambda x: x.to_dict(orient='records'))

        training_log = pd.concat([pd.DataFrame(log[i]) for i in range(2)])
        test_log = pd.concat([pd.DataFrame(log[i]) for i in range(2, 100)])
        # when process is discovered, should be perfect fitting to traces:
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        dcr, la = apply(training_log,post_process={'roles'})

        from pm4py.conformance import conformance_dcr
        res = conformance_dcr(test_log, dcr,return_diagnostics_dataframe=True)
        # change assertion, it should check for each trace and its fitness
        # this has been implemented as it allows us to check the shape of the template more accurately

        print(res)

    def test_rule_checking_role_conformance(self):
        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, la = pm4py.discover_dcr(log,process_type='roles')
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # change assertion, it should check for each trace and its fitness
        res = conf_alg(log, dcr)
        print(res[0])


    def test_rule_checking_with_role_attribute(self):
        # given a DCR graph and a event log
        log = pd.read_csv("../input_data/mobis/mobis_challenge_log_2019.csv", sep=";")
        log = pm4py.format_dataframe(log, case_id='case', activity_key='activity', timestamp_key='start')
        log = log.groupby("case:concept:name").apply(lambda x: x.to_dict(orient='records'))
        training_log = pd.concat([pd.DataFrame(log[i]) for i in range(3)])
        test_log = pd.concat([pd.DataFrame(log[i]) for i in range(3,10)])
        dcr, la = pm4py.discover_dcr(training_log, process_type='roles')
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # change assertion, it should check for each trace and its fitness
        res = conf_alg(training_log, dcr)
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'],True)
        #then conformance is perfect, same log used for mining i used for conformance check

    def test_rule_checking_with_deviation(self):
        # this will test if the log, can give feed back on errors of roles not given in the log
        # focus on roles in log and role assignment
        # given the mobis event log
        log = pd.read_csv("../input_data/mobis/mobis_challenge_log_2019.csv", sep=";")
        #needs to be reformated, makes for easy use, makes it safe such that the dtypes are correct for use
        log = pm4py.format_dataframe(log, case_id='case', activity_key='activity', timestamp_key='start')

        # group the log into a training log, and a test log
        log = log.groupby("case:concept:name").apply(lambda x: x.to_dict(orient='records'))
        training_log = pd.concat([pd.DataFrame(log[i]) for i in range(3)])
        test_log = pd.concat([pd.DataFrame(log[i]) for i in range(3, 10)])

        # replace a role
        training_log = training_log.replace(to_replace='Manager', value='Employee', regex=True)

        #perform the training log
        dcr, la = pm4py.discover_dcr(training_log, process_type='roles')
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # change assertion, it should check for each trace and its fitness
        res = conf_alg(test_log, dcr)
        for i in res:
            self.assertNotEqual(int(i['dev_fitness']), 1)
            self.assertFalse(i['is_fit'], )


    def test_run_traces_for_compliance(self):
        #for compliance, we want to run traces from a ground truth log
        # we had to test with the pdc 2019 logs for reference to the implementations
        #given a training log and trug log
        training_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Training Logs/pdc_2019_1.xes')
        truth_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Ground Truth Logs/pdc_2019_1.xes')

        # load in a timestamp, requirement for the library
        time1 = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        time2 = pd.date_range('2018-04-09', periods=len(truth_log), freq='20min')
        training_log['time:timestamp'] = time1
        truth_log['time:timestamp'] = time2

        truth_log = pm4py.convert_to_event_log(truth_log)
        #when model is discovered
        from pm4py.discovery import discover_dcr
        dcr, la = discover_dcr(training_log)
        from pm4py.algo.evaluation.compliance.variants.confusion_matrix import compliancechecker
        check = compliancechecker()
        res = check.compliant_traces(dcr, truth_log)

        print("accuracy: "+str(res.computeAccuracy()))
        print("recall: "+str(res.computeRecall()))
        print("precision: "+str(res.computePrecision()))
        # then it should return a numerical value for compliance
        # pdc in the paper has been told to have 45 true positive and 45 true negatives
        # So it is a good loog to test functionality for, as we know what the output should be
        self.assertEqual(res.computeAccuracy(), float(1))
        self.assertEqual(res.computeRecall(), float(1))
        self.assertEqual(res.computePrecision(), float(1))

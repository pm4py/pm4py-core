import os
import unittest
import pandas as pd
import pm4py
from pm4py.utils import get_properties


class Test_conformance_dcr(unittest.TestCase):

    def test_rule_checking_no_constraints(self):
        # given a dcr graph
        log = pm4py.read_xes("../input_data/running-example.xes")
        dcr, la = pm4py.discover_dcr(log)

        # when running getConstraints
        no = dcr.getConstraints()

        # then object, should contain 31 constraints
        self.assertTrue(no == 31)

    def test_rule_checking_conformance(self):
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg

        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # when process is discovered and check conformance
        dcr, la = pm4py.discover_dcr(log)
        res = conf_alg(log, dcr, parameters=None)
        # then the models should have perfect fitness
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'], True)

    def test_rule_checking_dataframe(self):
        from pm4py.conformance import conformance_dcr

        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # when process is discovered, check conformance to return dianostics
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        dcr, la = pm4py.discover_dcr(log)
        res = conformance_dcr(log, dcr, return_diagnostics_dataframe=True)
        # then the models should have perfect fitness
        self.assertIsInstance(res, pd.DataFrame)

    def test_condition_violation(self):
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg

        # given a log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graph
        dcr, _ = pm4py.discover_dcr(log)

        # and a log with 1 trace with condition violation
        log = log.drop(log[log['case:concept:name'] != "1"].index, axis="index")
        log = log.drop(log[log['concept:name'] == "register request"].index, axis="index")
        # when conformance is checked
        res = conf_alg(log, dcr)
        # fitness is not 1.0, and contains 2 conditions violations
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in res[0]['deviations']:
            if i[0] == 'conditionViolation':
                collect.append(i[0])
        self.assertIn('conditionViolation', collect)
        self.assertTrue(len(collect) == 2)

    def test_response_violation(self):
        # given a log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graph
        dcr, la = pm4py.discover_dcr(log)

        # and a log with 1 trace with pending violations
        log = log.drop(log[log['case:concept:name'] != "1"].index, axis="index")
        log = log.drop(log[log['concept:name'] == "decide"].index, axis="index")
        log = log.drop(log[log['concept:name'] == "reject request"].index, axis="index")

        # when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        res = conf_alg(log, dcr)

        # fitness is not 1.0 and contains 2 response Violations
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in res[0]['deviations']:
            if i[0] == 'responseViolation':
                collect.append(i[0])

        self.assertIn('responseViolation', collect)
        self.assertEqual(len(collect), 2)

    def test_exclude_violation(self):
        # given A log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graphs
        dcr, la = pm4py.discover_dcr(log)

        # and a log with 1 trace containing only register request, exclude violations
        log = log.drop(log[log['concept:name'] != "register request"].index, axis="index")
        new = {'case:concept:name': [1 for i in range(len(log))]}
        log['case:concept:name'] = pd.DataFrame(new).values

        # when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        res = conf_alg(log, dcr)

        # fitness is not 1, and has 1 exclude violations
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in res[0]['deviations']:
            if i[0] == 'excludeViolation':
                collect.append(i[0])
        self.assertIn('excludeViolation', collect)
        self.assertEqual(1, len(collect))

    def test_include_violation(self):
        # given a log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graph
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        dcr, la = apply(log)

        # and a log with 1 trace with include violation
        log = log[log['case:concept:name'] == "3"]
        row = log[log['concept:name'] == "reinitiate request"]
        log = pd.concat([log.iloc[:4], row, log.iloc[4:]]).reset_index(drop=True)

        # when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        res = conf_alg(log, dcr)

        # then it should not have perfect fitness, with an include violations
        # note that include violation, are tightly associated with exclude violation
        # it triggers, if an event should have occured before this event to include it
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in res[0]['deviations']:
            if i[0] == 'includeViolation':
                collect.append(i[0])
        self.assertIn('includeViolation', collect)
        self.assertEqual(1, len(collect))

    def test_get_constraint_for_roles(self):
        # given a dcr graph
        log = pm4py.read_xes("../input_data/running-example.xes")
        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")
        # when running getConstraints
        no = dcr.getConstraints()
        # then object, should contain the roleAssignment
        # 31 original constraints, but also, 19 additional role assignments
        self.assertTrue(no == 50)

    def test_rule_checking_role_conformance(self):
        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")

        # when conformance is check with roles on same log used for mining
        # should
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        parameters = get_properties(log, group_key="org:resource")
        res = conf_alg(log, dcr, parameters=parameters)
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

    def test_conformance_with_group_key(self):
        # check if conformance work with group_key as standard input
        log = pm4py.read_xes("../input_data/receipt.xes")
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'})
        res = pm4py.conformance_dcr(log, dcr)
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

    def test_rule_checking_event_with_not_included_role(self):
        # Given an event log and discovering a dcr
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")
        from pm4py.algo.conformance.dcr.variants import classic
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # when the roles are changed and conformance is performed
        log = log.replace("Mike", "Brenda")
        parameters = get_properties(log, group_key="org:resource")
        res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should not be perfect
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        for i in res[0]['deviations']:
            self.assertEqual(i[0], 'roleViolation')

    def test_rule_checking_with_wrong_resource(self):
        # Given an event log and discovering a dcr
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")
        from pm4py.algo.conformance.dcr.variants import classic
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # when the roles are changed and conformance is performed
        log = log.replace("Sara", "Mike")

        parameters = get_properties(log, group_key="org:resource")
        res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should not be perfect
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        for i in res[0]['deviations']:
            self.assertEqual(i[0], 'roleViolation')

    def test_rule_checking_with_log_missing_resource(self):
        # Given an event log and discovering a dcr
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")
        from pm4py.algo.conformance.dcr.variants import classic
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # when the roles are changed and conformance is performed
        log = log.replace("Sara", float("nan"))
        parameters = get_properties(log, group_key="org:resource")
        res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should not be perfect
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        for i in res[0]['deviations']:
            self.assertEqual(i[0], 'roleViolation')

    def test_conformance_event_with_no_role(self):
        # Given an event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        training_log = log.copy()
        # and one event has no role
        new_row = (log[log['concept:name'] == "reinitiate request"])
        new_row = new_row.replace("Sara", float("nan"))
        for index, _ in new_row.iterrows():
            training_log.iloc[index] = new_row.loc[index]

        # given the DCR process is discovered
        dcr, la = pm4py.discover_dcr(training_log, process_type='roles', group_key="org:resource")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # and a log with 1 trace
        log = (log[log['case:concept:name'] == "3"])
        # when conformance is checked
        parameters = get_properties(log, group_key="org:resource")
        res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should be perfect, as events with no roles, can be executed by anybody
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

    def fix_mobis_event_log(self, log):
        # found some erros in the log due check https://emisa-journal.org/emisa/article/view/247 for more information
        # this was log provided during this project
        # The following combination is not present in the text of the paper, so theres a good chance it's false
        log.loc[(log["concept:name"] == 'check if travel request needs preliminary price inquiry') & (
                log["org:role"] == "Employee"), 'org:role'] = float("nan")
        log.loc[(log["concept:name"] == 'decide on approval requirements') & (
                log["org:role"] == "Employee"), 'org:role'] = float("nan")
        return log

    def test_rule_checking_with_role_attribute(self):
        # given a DCR graph and a event log
        log = pd.read_csv("../input_data/mobis/mobis_challenge_log_2019.csv", sep=";")
        log = pm4py.format_dataframe(log, case_id='case', activity_key='activity', timestamp_key='start')

        log = self.fix_mobis_event_log(log)
        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key='org:role')
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # it returns deviation due to an event in the log, has instance of event with role and without
        parameters = pm4py.utils.get_properties(log, group_key='org:role')
        res = conf_alg(log, dcr, parameters=parameters)
        for i in res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

    def test_rule_checking_with_replaced_role(self):
        # given an event log
        log = pd.read_csv("../input_data/mobis/mobis_challenge_log_2019.csv", sep=";")
        log = pm4py.format_dataframe(log, case_id='case', activity_key='activity', timestamp_key='start')

        # clean log
        log = self.fix_mobis_event_log(log)

        dcr, la = pm4py.discover_dcr(log, process_type='roles', group_key="org:role")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        log = log.replace("Manager", "Boss")
        log = log[log['case:concept:name'] == '3887']
        # it returns deviation due to an event in the log, has instance of event with role and without
        parameters = get_properties(log, group_key="org:role")
        res = conf_alg(log, dcr, parameters=parameters)
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in res:
            for j in i['deviations']:
                collect.append(j[0])
        self.assertIn('roleViolation', collect)
        self.assertEqual(1, len(collect))

    def test_conformance_with_test_log(self):
        # given an event log
        training_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Training Logs/pdc_2019_1.xes')
        test_log = pm4py.read_xes('../input_data/pdc/pdc_2019/Test Logs/pdc_2019_1.xes')

        # load in a timestamp, requirement for the library
        time1 = pd.date_range('2018-04-09', periods=len(training_log), freq='20min')
        time2 = pd.date_range('2018-04-09', periods=len(test_log), freq='20min')
        training_log['time:timestamp'] = time1
        test_log['time:timestamp'] = time2

        # when a process is discovered, and analysed for conformance
        dcr, _ = pm4py.discover_dcr(training_log)
        res = pm4py.conformance_dcr(test_log, dcr)
        collect = 0
        for i in res:
            collect += i['dev_fitness']
        collect = collect / len(res)
        self.assertNotEqual(collect, 1.0)

    def test_conformance_with_dcr(self):
        #test to see if the conformance checker can run an imported graph
        from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as importer
        dcr = importer("../input_data/DCR_test_Claims/DCR_test_Claims.xml")
        log = pm4py.read_xes("../input_data/DCR_test_Claims/event_log.xes")
        log = log[log["lifecycle:transition"] != "complete"]
        res = pm4py.conformance_dcr(log,dcr)


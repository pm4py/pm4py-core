import os
import unittest
import pandas as pd
import pm4py
from pm4py.utils import get_properties

class TestConformanceDCR(unittest.TestCase):
    def test_rule_checking_no_constraints(self):
        # given a dcr graph
        log = pm4py.read_xes("../input_data/running-example.xes")
        dcr, _ = pm4py.discover_dcr(log)
        # when running getConstraints
        no = dcr.get_constraints()
        # then object, should contain 31 constraints
        self.assertTrue(no == 31)

        del log
        del dcr
        del no

    def test_rule_checking_conformance(self):
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg

        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # when process is discovered and check conformance
        dcr, _ = pm4py.discover_dcr(log)
        conf_res = conf_alg(log, dcr, parameters=None)
        # then the models should have perfect fitness
        for i in conf_res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'], True)

        del log
        del dcr
        del conf_res

    def test_rule_checking_dataframe(self):
        from pm4py.conformance import conformance_dcr

        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # when process is discovered, check conformance to return dianostics
        dcr, _ = pm4py.discover_dcr(log)
        conf_res = conformance_dcr(log, dcr, return_diagnostics_dataframe=True)
        # then the models should have perfect fitness
        self.assertIsInstance(conf_res, pd.DataFrame)

        del log
        del dcr
        del conf_res

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
        conf_res = conf_alg(log, dcr)
        # fitness is not 1.0, and contains 2 conditions violations
        collect = 0
        for i in conf_res:
            collect += i['dev_fitness']
        collect = collect / len(conf_res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in conf_res[0]['deviations']:
            if i[0] == 'conditionViolation':
                collect.append(i[0])
        self.assertIn('conditionViolation', collect)
        self.assertTrue(len(collect) == 2)

        del log
        del dcr
        del conf_res
        del collect

    def test_response_violation(self):
        # given a log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graph
        dcr, _ = pm4py.discover_dcr(log)

        # and a log with 1 trace with pending violations
        log = log.drop(log[log['case:concept:name'] != "1"].index, axis="index")
        log = log.drop(log[log['concept:name'] == "decide"].index, axis="index")
        log = log.drop(log[log['concept:name'] == "reject request"].index, axis="index")

        # when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        conf_res = conf_alg(log, dcr)

        # fitness is not 1.0 and contains 2 response Violations
        collect = 0
        for i in conf_res:
            collect += i['dev_fitness']
        collect = collect / len(conf_res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in conf_res[0]['deviations']:
            if i[0] == 'responseViolation':
                collect.append(i[0])

        self.assertIn('responseViolation', collect)
        self.assertEqual(len(collect), 2)

        del log
        del dcr
        del conf_res
        del collect



    def test_exclude_violation(self):
        # given A log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graphs
        dcr, _ = pm4py.discover_dcr(log)

        # and a log with 1 trace containing only register request, exclude violations
        log = log.drop(log[log['concept:name'] != "register request"].index, axis="index")
        new = {'case:concept:name': [1 for i in range(len(log))]}
        log['case:concept:name'] = pd.DataFrame(new).values

        # when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        conf_res = conf_alg(log, dcr)

        # fitness is not 1, and has 1 exclude violations
        collect = 0
        for i in conf_res:
            collect += i['dev_fitness']
        collect = collect / len(conf_res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in conf_res[0]['deviations']:
            if i[0] == 'excludeViolation':
                collect.append(i[0])
        self.assertIn('excludeViolation', collect)
        self.assertEqual(1, len(collect))

        del log
        del dcr
        del conf_res
        del collect

    def test_include_violation(self):
        # given a log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and a DCR graph
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        dcr, _ = apply(log)

        # and a log with 1 trace with include violation
        log = log[log['case:concept:name'] == "3"]
        row = log[log['concept:name'] == "reinitiate request"]
        log = pd.concat([log.iloc[:4], row, log.iloc[4:]]).reset_index(drop=True)

        # when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        conf_res = conf_alg(log, dcr)

        # then it should not have perfect fitness, with an include violations
        # note that include violation, are tightly associated with exclude violation
        # it triggers, if an event should have occured before this event to include it
        collect = 0
        for i in conf_res:
            collect += i['dev_fitness']
        collect = collect / len(conf_res)
        self.assertNotEqual(collect, 1.0)
        collect = []
        for i in conf_res[0]['deviations']:
            if i[0] == 'includeViolation':
                collect.append(i[0])
        self.assertIn('includeViolation', collect)
        self.assertEqual(1, len(collect))

        del log
        del dcr
        del conf_res
        del collect

    def test_get_constraint_for_roles(self):
        # given a dcr graph
        log = pm4py.read_xes("../input_data/running-example.xes")
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")
        # when running getConstraints
        no = dcr.get_constraints()
        # then object, should contain the roleAssignment
        # 31 original constraints, but also, 19 additional role assignments
        self.assertTrue(no == 50)

        del log
        del dcr
        del no

    def test_rule_checking_role_conformance(self):
        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")

        # when conformance is check with roles on same log used for mining
        # should
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        parameters = get_properties(log, group_key="org:resource")
        conf_res = conf_alg(log, dcr, parameters=parameters)
        for i in conf_res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

        del log
        del dcr
        del conf_res
        del parameters

    def test_conformance_with_group_key(self):
        # check if conformance work with group_key as standard input
        log = pm4py.read_xes("../input_data/receipt.xes")
        log.replace("Group 1",float("nan"))

        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'})
        conf_res = pm4py.conformance_dcr(log, dcr)

        for i in conf_res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

        del log
        del dcr
        del conf_res



    def test_rule_checking_event_with_not_included_role(self):
        # Given an event log and discovering a dcr
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # when the roles are changed and conformance is performed
        log = log.replace("Mike", "Brenda")
        parameters = get_properties(log, group_key="org:resource")
        conf_res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should not be perfect
        for i in conf_res:
            self.assertNotEqual(i["dev_fitness"], 1.0)

        del log
        del dcr
        del conf_res


    def test_rule_checking_with_wrong_resource(self):
        # Given an event log and discovering a dcr
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # when the roles are changed and conformance is performed
        log = log.replace("Sara", "Mike")

        parameters = get_properties(log, group_key="org:resource")
        conf_res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should not be perfect
        for i in conf_res:
            self.assertNotEqual(i["dev_fitness"], 1.0)
        for i in conf_res[0]['deviations']:
            self.assertEqual(i[0], 'roleViolation')

        del log
        del dcr
        del conf_res

    def test_rule_checking_with_log_missing_resource(self):
        # Given an event log and discovering a dcr
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, _ = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # when the roles are changed and conformance is performed
        log = log.replace("Sara", float("nan"))
        parameters = get_properties(log, group_key="org:resource")
        conf_res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should not be perfect
        for i in conf_res:
            self.assertNotEqual(i["dev_fitness"], 1.0)
        for i in conf_res[0]['deviations']:
            self.assertEqual(i[0], 'roleViolation')

        del dcr
        del log
        del conf_res
        del parameters


    def test_conformance_event_with_no_role(self):
        # Given an event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))

        # and one event has no role
        new_row = (log[log['concept:name'] == "reinitiate request"])
        new_row = new_row.replace("Sara", float("nan"))
        for index, _ in new_row.iterrows():
            log.iloc[index] = new_row.loc[index]

        # given the DCR process is discovered
        dcr, _ = pm4py.discover_dcr(log, process_type='roles', group_key="org:resource")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # and a log with 1 trace
        log = (log[log['case:concept:name'] == "3"])
        # when conformance is checked
        parameters = get_properties(log, group_key="org:resource")
        conf_res = conf_alg(log, dcr, parameters=parameters)
        # then the fitness should be perfect, as events with no roles, can be executed by anybody
        for i in conf_res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

        del dcr
        del log
        del conf_res
        del parameters

    def test_rule_checking_with_role_attribute(self):
        # given a DCR graph and a event log
        # check if conformance work with group_key as standard input
        log = pm4py.read_xes("../input_data/receipt.xes")
        log = log.rename(columns={"org:group": "org:role"})
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key='org:role')
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        # it returns deviation due to an event in the log, has instance of event with role and without
        parameters = pm4py.utils.get_properties(log, group_key='org:role')
        conf_res = conf_alg(log, dcr, parameters=parameters)
        for i in conf_res:
            self.assertEqual(int(i['dev_fitness']), 1)
            self.assertTrue(i['is_fit'])

        del dcr
        del log
        del conf_res
        del parameters

    def test_rule_checking_with_replaced_role(self):
        # given an event log
        log = pm4py.read_xes("../input_data/receipt.xes")
        log = log.rename(columns={"org:group": "org:role"})
        #with a role missing
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:role")

        log = log.replace("Group 14","Group 2")
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg

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
        self.assertEqual(5, len(collect))

        del dcr
        del log
        del res
        del collect
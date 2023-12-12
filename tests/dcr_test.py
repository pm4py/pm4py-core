import os
import unittest
import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.objects.dcr.obj import DcrGraph, dcr_template
import pandas as pd
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.algo.conformance.alignments.dcr.variants.optimal import Alignment
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.dcr.exporter import exporter as dcr_exporter

class TestDiscoveryDCR(unittest.TestCase):
    def check_if_dcr_is_equal(self, dcr1, dcr2):
        self.assertEqual(len(dcr1.events), len(dcr2.events))
        for i, j in zip(dcr1.conditions, dcr2.conditions):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.conditions.get(i), dcr2.conditions.get(j)):
                self.assertEqual(k, l)

        for i, j in zip(dcr1.responses, dcr2.responses):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.responses.get(i), dcr2.responses.get(j)):
                self.assertEqual(k, l)

        for i, j in zip(dcr1.includes, dcr2.includes):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.includes.get(i), dcr2.includes.get(j)):
                self.assertEqual(k, l)

        for i, j in zip(dcr1.excludes, dcr2.excludes):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.excludes.get(i), dcr2.excludes.get(j)):
                self.assertEqual(k, l)

    def test_basic_discover_new_dcr_structure(self):
        # test to perform if the basic structure holdes all values needed and is mined correctly
        # given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        # when mined
        dcr, _ = apply(log, dcr_discover, findAdditionalConditions=False)
        # each unique events should be saved in the graph
        self.assertEqual(set(log['concept:name'].unique()), dcr.events)
        # it should have mined relations for activities,

        # We want to make sure, that the DCR object store relations
        self.assertNotEqual(len(dcr.conditions), 0)
        self.assertNotEqual(len(dcr.responses), 0)
        self.assertNotEqual(len(dcr.includes), 0)
        self.assertNotEqual(len(dcr.excludes), 0)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.events))

        del dcr
        del log

    def test_basic_discover_with_additionalconditions(self):
        # test to see if the DCR graphs has been mine correctly with additional conditions
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        dcr, _ = apply(log)
        # each unique events should be saved in the graph
        self.assertEqual(set(log['concept:name'].unique()), dcr.events)
        # it should have mined relations for activities,

        # We want to make sure, that the DCR object store relations
        self.assertNotEqual(len(dcr.conditions), 0)
        self.assertNotEqual(len(dcr.responses), 0)
        self.assertNotEqual(len(dcr.includes), 0)
        self.assertNotEqual(len(dcr.excludes), 0)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.events))

        del dcr
        del log

    def test_basic_disCover(self):
        log1 = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr1, _ = apply(log1, dcr_discover)

        log2 = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr2, _ = apply(log2, dcr_discover)
        self.check_if_dcr_is_equal(dcr1, dcr2)

        del log1
        del dcr1
        del log2
        del dcr2

    def test_role_mining(self):
        # introduce roles in DCR graphs
        # given a DCR graph
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        # when mined, with post_process roles
        parameters = get_properties(log, group_key="org:resource")
        dcr, _ = apply(log, post_process={'roles'}, parameters=parameters)
        # these attributes, will not be empty
        self.assertNotEqual(len(dcr.roles), 0)
        self.assertNotEqual(len(dcr.principals), 0)
        self.assertNotEqual(len(dcr.role_assignments), 0)
        # no roles are given, so principals and roles should be equal
        self.assertEqual(dcr.principals, dcr.roles)

        del log
        del dcr

    def test_role_mining_receipt(self):
        # Given an event log
        log = pm4py.read_xes(os.path.join("input_data", "receipt.xes"))
        # when process is discovered
        dcr1, _ = pm4py.discover_dcr(log, process_type={'roles'})
        dcr2, _ = pm4py.discover_dcr(log, process_type={'roles'})
        # then the two model should be equal
        self.assertEqual(dcr1.roles, dcr2.roles)
        self.assertEqual(dcr1.principals, dcr2.principals)
        self.assertNotEqual(dcr1.roles, dcr1.principals)
        self.assertEqual(dcr1.role_assignments, dcr2.role_assignments)

        del log
        del dcr1
        del dcr2

    def test_role_mining_with_roles(self):
        # given an event log with role attribute
        log = pm4py.read_xes("input_data/receipt.xes")
        # when the dcr is mined
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'})

        # then roles, principals and roleAssignment should have some values
        # additionally, a org:role is provided, therefore principals and roles are different
        roles = pm4py.get_event_attribute_values(log, attribute="org:group")
        principals = pm4py.get_event_attribute_values(log, attribute="org:resource")
        self.assertEqual(dcr.roles, set(roles.keys()))
        self.assertEqual(dcr.principals, set(principals.keys()))
        self.assertNotEqual(len(dcr.role_assignments), 0)
        self.assertNotEqual(dcr.roles, dcr.principals)

        del log
        del dcr
        del roles
        del principals

    def test_role_mining_with_no_roles_or_resources(self):
        # if a person tries to mine for roles, but no roles or resources exist in the event log
        log = pm4py.read_xes(os.path.join('input_data', 'running-example.xes'))
        # drop org:resource column
        log = log.drop(columns=['org:resource'])
        # when the miner is then performed
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        with self.assertRaises(ValueError) as context:
            parameters = get_properties(log, group_key="org:resource")
            apply(log, dcr_discover, post_process={'roles'}, parameters=parameters)
        self.assertTrue(
            'input log does not contain attribute identifiers for resources or roles' in str(context.exception))

        del log


    def test_role_mining_activity_without_role(self):
        # Given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        # and one event has no role
        new_row = (log[log['concept:name'] == "reinitiate request"])
        new_row = new_row.replace("Sara", float("nan"))
        for index, _ in new_row.iterrows():
            log.iloc[index] = new_row.loc[index]

        # when process is discovered
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key='org:resource')
        # then reinititate request no longer has the orginal assigned role
        self.assertNotIn("reinitiate request", dcr.role_assignments['Sara'])

        del log
        del new_row
        del dcr


class TestObjSematics(unittest.TestCase):
    def test_getitem(self):
        # given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        # when a dcr is mine
        dcr, _ = apply(log, dcr_discover)
        # then dcr graph should be able to be called as a dictionary
        self.assertEqual(dcr['conditionsFor'], dcr.conditions)

        del log
        del dcr

    def test_getitem_inheritance(self):
        # given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        # when mined
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")
        # getitem should be able to call the additional variables associated with the role object
        self.assertEqual(dcr['roles'], dcr.roles)
        self.assertEqual(dcr['principals'], dcr.principals)
        self.assertEqual(dcr['roleAssignments'], dcr.role_assignments)

        del log
        del dcr

    def test_dcr_semantics_enabled(self):
        # given an eventlog
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, _ = apply(log, dcr_discover)
        # when an event is check for being enabled
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        # Then register request should return true, and other event has yet met conditions is false
        self.assertTrue(sem.is_enabled(log.iloc[0]["concept:name"], dcr))
        self.assertFalse(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

        del log
        del dcr
        del sem

    def test_dcr_execution_semantic(self):
        # given a graph from the DisCover miner
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, _ = apply(log, dcr_discover)
        # When event is executed, the event that has the event as a condition can then be executed
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        if sem.is_enabled(log.iloc[0]["concept:name"], dcr):
            dcr = sem.execute(dcr, log.iloc[0]["concept:name"])

        self.assertTrue(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

        del log
        del dcr
        del sem

    def test_dcr_is_accepting_semantic(self):
        # given a DCR graph discovered from Discover, is always initially accepting
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, _ = apply(log, dcr_discover)
        # then the DCR is accepting
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        self.assertTrue(sem.is_accepting(dcr))

        del log
        del dcr
        del sem

    def test_dcr_is_accepting_response_pending(self):
        # given a DCR graph discovered from Discover, is always initially accepting
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, _ = apply(log, dcr_discover)
        # when an event triggers a response relation
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        sem.execute(dcr, "register request")
        self.assertFalse(sem.is_accepting(dcr))

        del log
        del dcr
        del sem

    def test_label_mapping_to_activity(self):
        #given a simple dcr
        dcr = DcrGraph()
        dcr.events.add("event0")
        dcr.events.add("event1")
        dcr.events.add("event2")
        dcr.labels.add("A")
        dcr.labels.add("B")
        dcr.labels.add("C")
        dcr.label_mapping["A"] = {"event0"}
        dcr.label_mapping["B"] = {"event1"}
        dcr.label_mapping["C"] = {"event2"}
        # when labels are retried for the label mapping
        # then all the labels retrieve should exist in labels

        for i in dcr.events:
            act = dcr.get_activity(i)
            self.assertIsInstance(i,str)
            self.assertTrue(act in dcr.labels)

        del dcr

    def test_label_Mapping_to_eventID(self):
        # given a simple dcr
        dcr = DcrGraph()
        dcr.events.add("event0")
        dcr.events.add("event1")
        dcr.events.add("event2")
        dcr.labels.add("A")
        dcr.labels.add("B")
        dcr.labels.add("C")
        dcr.label_mapping["A"] = {"event0"}
        dcr.label_mapping["B"] = {"event1"}
        dcr.label_mapping["C"] = {"event2"}
        # when labels are retried for the label mapping
        # then all the labels retrieve should exist in labels
        for i in dcr.labels:
            act = dcr.get_activity(i)
            self.assertIsInstance(i, str)
            self.assertTrue(act in dcr.labels)

        del dcr

    def test_pending_event(self):
        from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as import_apply
        # given a dcr graph and event log
        # we use this as it provides an dcr graph, with eventIDs and labels and label mapping
        dcr = import_apply('input_data/pendingEvent.xml')
        self.assertEqual(1, len(dcr.marking.pending))

        del dcr

    def test_instantiate_object(self):
        dcr1 = DcrGraph()
        dcr2 = DcrGraph(dcr_template)
        # both empty should be equal
        self.assertEqual(dcr1, dcr2)

        del dcr1
        del dcr2


from pm4py.utils import get_properties
class TestConformanceDCR(unittest.TestCase):
    def test_rule_checking_no_constraints(self):
        # given a dcr graph
        log = pm4py.read_xes("input_data/running-example.xes")
        dcr, _ = pm4py.discover_dcr(log)
        # when running getConstraints
        no = dcr.get_constraints()
        # then object, should contain 30 constraints
        self.assertTrue(no == 30)

        del log
        del dcr
        del no

    def test_rule_checking_conformance(self):
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg

        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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

    def test_exclude_violation2(self):
        # given A log with check ticket at end after it has been excluded
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        dcr, _ = pm4py.discover_dcr(log)
        log = log[log['case:concept:name'] == "1"]
        row = log[log['concept:name'] == "check ticket"]
        log = pd.concat([log,row]).reset_index(drop=True)

        #when conformance is checked
        from pm4py.algo.conformance.dcr.algorithm import apply as conf_alg
        conf_res = conf_alg(log, dcr)

        # fitness is not 1, and has 1 exclude violation
        collect = []
        for i in conf_res[0]['deviations']:
            if i[0] == 'excludeViolation':
                collect.append(i[0])
        self.assertIn('excludeViolation', collect)
        self.assertEqual(1, len(collect))

    def test_include_violation(self):
        # given a log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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
        log = pm4py.read_xes("input_data/running-example.xes")
        dcr, _ = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")
        # when running getConstraints
        no = dcr.get_constraints()
        # then object, should contain the roleAssignment
        # 31 original constraints, but also, 19 additional role assignments
        self.assertTrue(no == 49)

        del log
        del dcr
        del no

    def test_rule_checking_role_conformance(self):
        # given a DCR graph and a event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
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
        log = pm4py.read_xes("input_data/receipt.xes")
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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
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
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

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
        log = pm4py.read_xes("input_data/receipt.xes")
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
        log = pm4py.read_xes("input_data/receipt.xes")
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

class TestAlignment(unittest.TestCase):

    def setUp(self):
        log_path = os.path.join("input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        if isinstance(self.log, pd.DataFrame):
            self.log = log_converter.apply(self.log)
        self.dcr_result = apply(self.log, pm4py.algo.discovery.dcr_discover.variants.dcr_discover)
        self.dcr = self.dcr_result[0]
        self.assertIsNotNone(self.dcr)
        self.first_trace = self.log[0]

    def test_initial_alignment(self):
        graph_handler = self.create_graph_handler(self.dcr)
        trace_handler = self.create_trace_handler(self.first_trace)

        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.validate_alignment(aligned_traces)

        del graph_handler
        del trace_handler
        del alignment_obj
        del aligned_traces

    def test_trace_alignments(self):
        for trace in self.log:
            self.check_trace_alignment(trace)

    def test_alignment_costs(self):
        graph_handler = self.create_graph_handler(self.dcr)
        trace_handler = self.create_trace_handler(self.first_trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.check_alignment_cost(aligned_traces)

        del graph_handler
        del trace_handler
        del alignment_obj
        del aligned_traces

    def test_Check_model_moves(self):
        # remove event from log
        trace = [e["concept:name"] for e in self.first_trace]
        trace.remove("check ticket")
        graph_handler = self.create_graph_handler(self.dcr)
        trace_handler = self.create_trace_handler(trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.check_alignment_cost(aligned_traces)
        self.check_trace_alignment(trace)

        del trace
        del graph_handler
        del trace_handler
        del alignment_obj
        del aligned_traces

    def test_Check_log_moves(self):
        #remove event from log
        trace = [e["concept:name"] for e in self.first_trace]
        trace.append("check ticket")
        graph_handler = self.create_graph_handler(self.dcr)
        trace_handler = self.create_trace_handler(trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.check_alignment_cost(aligned_traces)
        self.check_trace_alignment(trace)

        del trace
        del graph_handler
        del trace_handler
        del alignment_obj
        del aligned_traces

    def test_combination(self):
        #remove event from log
        trace = [e["concept:name"] for e in self.first_trace]
        trace[3] = "reject request"
        trace.insert(5,"register request")
        trace.pop(8)
        graph_handler = self.create_graph_handler(self.dcr)
        trace_handler = self.create_trace_handler(trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()

        self.check_alignment_cost(aligned_traces)
        self.check_trace_alignment(trace)

        del trace
        del graph_handler
        del trace_handler
        del alignment_obj
        del aligned_traces

    def test_log_simple_interface(self):
        log_path = os.path.join("input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        align_res = pm4py.optimal_alignment_dcr(self.log, self.dcr)
        for row in align_res:
            self.assertTrue(row['fitness'] == 1.0)
        del log_path
        del align_res

    def test_fitness(self):
        align_res = pm4py.optimal_alignment_dcr(self.first_trace, self.dcr)
        for row in align_res:
            self.assertTrue(row['fitness'] == 1.0)
        del align_res

    def test_return_dataframe(self):
        log_path = os.path.join("input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        align_res = pm4py.optimal_alignment_dcr(self.log, self.dcr, return_diagnostics_dataframe=True)
        self.assertIsInstance(align_res,pd.DataFrame)

        for index,row in align_res.iterrows():
            self.assertTrue(row['fitness'] == 1.0)
        del log_path
        del align_res

    @staticmethod
    def create_graph_handler(dcr_graph):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.DCRGraphHandler(dcr_graph)

    @staticmethod
    def create_trace_handler(trace):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.TraceHandler(trace, 'concept:name')

    @staticmethod
    def create_log_handler(log):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.LogAlignment(log, 'concept:name')

    def validate_alignment(self, aligned_traces):
        self.assertIsNotNone(aligned_traces)
        self.assertIsInstance(aligned_traces, dict)
        self.assertIn('alignment', aligned_traces)

    def check_trace_alignment(self, trace):
        graph_handler = self.create_graph_handler(self.dcr)
        trace_handler = self.create_trace_handler(trace)

        alignment_obj = Alignment(graph_handler, trace_handler)
        dcr_trace_result = alignment_obj.apply_trace()

        self.assertIsNotNone(dcr_trace_result)
        self.assertIn('alignment', dcr_trace_result)
        self.assertGreaterEqual(len(dcr_trace_result['alignment']),len(trace))

        if len(trace) > 0:
            self.assertNotEqual(len(dcr_trace_result['alignment']), 0)

    def check_alignment_cost(self, aligned_traces):
        alignment = aligned_traces['alignment']
        alignment_cost = aligned_traces.get('cost', float('inf'))
        self.assertEqual(alignment_cost, aligned_traces.get('global_min', float('inf')))
        model_moves = sum(1 for move in alignment if move[0] == '>>')
        log_moves = sum(1 for move in alignment if move[1] == '>>')
        expected_cost = model_moves + log_moves
        self.assertEqual(expected_cost, alignment_cost)

    def test_return_datafrane_alignment(self):
        log_path = os.path.join("input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        res = pm4py.optimal_alignment_dcr(self.log, self.dcr, return_diagnostics_dataframe=True)
        self.assertIsInstance(res,pd.DataFrame)
        for index,row in res.iterrows():
            self.assertTrue(row['fitness'] == 1.0)

class TestImportExportDCR(unittest.TestCase):

    def setUp(self) -> None:
        import urllib.request
        url = "https://data.4tu.nl/file/33632f3c-5c48-40cf-8d8f-2db57f5a6ce7/643dccf2-985a-459e-835c-a82bce1c0339"
        self.sepsis = "input_data/Sepsis cases - Event Log.xes.gz"
        with urllib.request.urlopen(url) as response, open("input_data/Sepsis cases - Event Log.xes.gz", "wb") as out_file:
            out_file.write(response.read())

        self.test_file = ''
        self.second_test_file = ''

    def test_exporter_to_xml_simple(self):
        event_log_file = os.path.join("input_data", "receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_xml_simple.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.test_file,variant=dcr_exporter.XML_SIMPLE, dcr_title='receipt_xml_simple')

        del log
        del dcr

    def test_import_export_xml_simple(self):
        event_log_file = os.path.join("input_data", "receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_xml_simple.xml")
        self.export_file_simple(event_log_file)
        dcr = pm4py.read_dcr_xml(self.test_file, variant=dcr_importer.Variants.XML_SIMPLE)
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.test_file,variant=dcr_exporter.Variants.XML_SIMPLE, dcr_title='receipt_xml_simple_exported')
        dcr_imported_after_export = pm4py.read_dcr_xml(self.test_file, variant=dcr_importer.Variants.XML_SIMPLE)
        self.assertEqual(len(dcr.__dict__), len(dcr_imported_after_export.__dict__))

        del dcr
        del dcr_imported_after_export

    # Events are not included (dashed lines) in the portal
    def test_xml_simple_to_dcr_js_portal(self):
        event_log_file = os.path.join("input_data", "receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_xml_simple.xml")
        self.export_file_simple(event_log_file)
        dcr = pm4py.read_dcr_xml(self.test_file, variant=dcr_importer.Variants.XML_SIMPLE)

        os.remove(self.test_file)

        self.test_file = os.path.join("test_output_data", "receipt_xml_simple_to_dcr_js_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.test_file,variant=dcr_exporter.Variants.DCR_JS_PORTAL, dcr_title='receipt_xml_simple_to_dcr_js_portal')

        del dcr

    def test_exporter_to_dcr_portal(self):
        event_log_file = os.path.join("input_data","Sepsis cases - Event Log.xes.gz")
        self.test_file = os.path.join("test_output_data", "sepsis_dcr_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.test_file,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='xml_2_dcr_portal')

        del log
        del dcr


    def test_importer_from_dcr_portal(self):
        event_log_file = os.path.join("input_data", "Sepsis cases - Event Log.xes.gz")
        self.test_file = os.path.join("test_output_data", "sepsis_dcr_portal.xml")
        self.export_file_dcr_portal(event_log_file)
        dcr = pm4py.read_dcr_xml(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
        self.assertIsNotNone(dcr)

        del event_log_file
        del dcr

    def test_import_export_dcr_portal(self):

        self.test_file = os.path.join("test_output_data", "sepsis_dcr_portal.xml")
        self.export_file_dcr_portal(self.sepsis)
        dcr = pm4py.read_dcr_xml(self.test_file)
        self.second_test_file = os.path.join("test_output_data", "sepsis_dcr_portal_exported.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.second_test_file,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='sepsis_dcr_portal_exported_xml')
        dcr_imported_after_export = pm4py.read_dcr_xml(self.second_test_file)
        self.assertEqual(len(dcr.__dict__), len(dcr_imported_after_export.__dict__))

        del dcr_imported_after_export
        del dcr

    def test_exporter_to_dcr_js_portal(self):
        event_log_file = os.path.join("input_data", "receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_dcr_js_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr, path=self.test_file, variant=dcr_exporter.Variants.DCR_JS_PORTAL, dcr_title='reviewing_exported_dcr_js_portal')

        del log
        del dcr

    def test_importer_from_dcr_js_portal(self):
        event_log_file = os.path.join("input_data", "receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_dcr_js_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr, path=self.test_file, variant=dcr_exporter.Variants.DCR_JS_PORTAL,
                            dcr_title='reviewing_exported_dcr_js_portal')
        dcr = pm4py.read_dcr_xml(os.path.join("test_output_data", "receipt_dcr_js_portal.xml"))
        self.assertIsNotNone(dcr)

        del dcr
        del log


    def test_import_export_dcr_js_portal(self):
        event_log_file = os.path.join("input_data","receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_dcr_js_portal.xml")
        self.export_file_dcr_js(event_log_file)
        dcr = pm4py.read_dcr_xml(self.test_file)
        self.second_test_file = os.path.join("test_output_data", "receipt_dcr_js_portal_exported.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.second_test_file,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='receipt_dcr_js_portal_exported')
        dcr_imported_after_export = pm4py.read_dcr_xml(self.second_test_file)
        self.assertEqual(len(dcr.__dict__), len(dcr_imported_after_export.__dict__))

        del dcr
        del dcr_imported_after_export

    def test_xml_dcr_portal_to_dcr_js_portal(self):
        self.test_file = os.path.join("test_output_data", "sepsis_dcr_portal.xml")
        self.export_file_dcr_portal(self.sepsis)
        dcr = pm4py.read_dcr_xml(self.test_file)
        self.second_test_file = os.path.join("test_output_data", "sepsis_dcr_js_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.second_test_file,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='sepsis_dcr_js_portal')

        del dcr

    def test_dcr_js_portal_to_xml_dcr_portal(self):
        event_log_file = os.path.join("input_data","receipt.xes")
        self.test_file = os.path.join("test_output_data", "receipt_dcr_js_portal.xml")
        self.export_file_dcr_js(event_log_file)
        dcr = pm4py.read_dcr_xml(self.test_file)

        self.second_test_file = os.path.join("test_output_data", "receipt_dcr_xml_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=self.second_test_file,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='receipt_dcr_xml_portal')

        del dcr

    def test_xes_to_xml_dcr_portal_to_dcr_js_portal(self):
        event_log_file = os.path.join("input_data", "running-example.xes")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)

        self.test_file = os.path.join("test_output_data", "running-example_dcr_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr, path=self.test_file, variant=dcr_exporter.XML_DCR_PORTAL,
                            dcr_title='running-example_dcr_portal')
        dcr_imported_after_export = pm4py.read_dcr_xml(self.test_file)
        self.second_test_file = os.path.join("test_output_data", "running-example_dcr_js_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr_imported_after_export, path=self.second_test_file,
                            variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='running-example_dcr_js_portal')

        del dcr
        del log
        del dcr_imported_after_export

    def export_file_simple(self, event_log_file):
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr, path=self.test_file, variant=dcr_exporter.XML_SIMPLE,
                            dcr_title='xml_simple')

    def export_file_dcr_portal(self, event_log_file):
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr, path=self.test_file, variant=dcr_exporter.XML_DCR_PORTAL,
                            dcr_title='xml_dcr_portal')

    def export_file_dcr_js(self, event_log_file):
        log = pm4py.read_xes(event_log_file)
        dcr, _ = apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr, path=self.test_file, variant=dcr_exporter.DCR_JS_PORTAL,
                            dcr_title='xml_dcr_js')

    def tearDown(self) -> None:
        os.remove("input_data/Sepsis cases - Event Log.xes.gz")
        if self.test_file != '':
            os.remove(self.test_file)
            self.test_file = ''
        if self.second_test_file != '':
            os.remove(self.second_test_file)
            self.second_test_file = ''


if __name__ == '__main__':
    unittest.main()

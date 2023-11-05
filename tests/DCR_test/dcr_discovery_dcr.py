import os
import unittest

import pandas as pd

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.utils import get_properties


class Test_discovery_dcr(unittest.TestCase):
    def check_if_dcr_is_equal(self, dcr1, dcr2):
        self.assertEqual(len(dcr1.events), len(dcr2.events))
        for i, j in zip(dcr1.conditionsFor, dcr2.conditionsFor):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.conditionsFor.get(i), dcr2.conditionsFor.get(j)):
                self.assertEqual(k, l)

        for i, j in zip(dcr1.responseTo, dcr2.responseTo):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.responseTo.get(i), dcr2.responseTo.get(j)):
                self.assertEqual(k, l)

        for i, j in zip(dcr1.includesTo, dcr2.includesTo):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.includesTo.get(i), dcr2.includesTo.get(j)):
                self.assertEqual(k, l)

        for i, j in zip(dcr1.excludesTo, dcr2.excludesTo):
            self.assertEqual(i, j)
            for k, l in zip(dcr1.excludesTo.get(i), dcr2.excludesTo.get(j)):
                self.assertEqual(k, l)


    def test_Basic_DisCoveR_new_DCR_structure(self):
        #test to perform if the basic structure holdes all values needed and is mined correctly
        # given an event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        # when mined
        dcr, la = apply(log, dcr_discover, findAdditionalConditions=False)
        # each unique events should be saved in the graph
        self.assertEqual(set(log['concept:name'].unique()), dcr.events)
        # it should have mined relations for activities,

        # We want to make sure, that the DCR object store relations
        self.assertNotEqual(len(dcr.conditionsFor), 0)
        self.assertNotEqual(len(dcr.responseTo), 0)
        self.assertNotEqual(len(dcr.includesTo), 0)
        self.assertNotEqual(len(dcr.excludesTo), 0)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.events))


    def test_Basic_DisCover_with_AdditionalConditions(self):
        #test to see if the DCR graphs has been mine correctly with additional conditions
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        dcr, la = apply(log)
        # each unique events should be saved in the graph
        self.assertEqual(set(log['concept:name'].unique()), dcr.events)
        # it should have mined relations for activities,

        # We want to make sure, that the DCR object store relations
        self.assertNotEqual(len(dcr.conditionsFor),0)
        self.assertNotEqual(len(dcr.responseTo),0)
        self.assertNotEqual(len(dcr.includesTo),0)
        self.assertNotEqual(len(dcr.excludesTo),0)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.events))


    def test_Basic_DisCover(self):
        log1 = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr1, la = apply(log1, dcr_discover)

        log2 = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr2, la = apply(log2, dcr_discover)
        self.check_if_dcr_is_equal(dcr1, dcr2)

    def test_role_mining(self):
        #introduce roles in DCR graphs
        #given a DCR graph
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        log = pm4py.convert_to_event_log(log)
        #when mined, with post_process roles
        parameters = get_properties(log,group_key="org:resource")
        dcr, la = apply(log, post_process={'roles'},parameters=parameters)
        #these attributes, will not be empty
        self.assertNotEqual(len(dcr.roles),0)
        self.assertNotEqual(len(dcr.principals),0)
        self.assertNotEqual(len(dcr.roleAssignments),0)
        # no roles are given, so principals and roles should be equal
        self.assertEqual(dcr.principals, dcr.roles)

    def test_role_mining_receipt(self):
        # Given an event log
        log = pm4py.read_xes(os.path.join("../input_data", "receipt.xes"))
        #when process is discovered
        dcr1, _ = pm4py.discover_dcr(log, process_type={'roles'})
        dcr2, _ = pm4py.discover_dcr(log, process_type={'roles'})
        # then the two model should be equal
        self.assertEqual(dcr1.roles,dcr2.roles)
        self.assertEqual(dcr1.principals, dcr2.principals)
        self.assertNotEqual(dcr1.roles,dcr1.principals)
        self.assertEqual(dcr1.roleAssignments, dcr2.roleAssignments)



    def test_role_mining_with_roles(self):
        # given an event log with role attribute
        log = pd.read_csv("../input_data/mobis/mobis_challenge_log_2019.csv",sep=";")
        log = pm4py.format_dataframe(log, case_id='case', activity_key='activity', timestamp_key='start')

        # when the dcr is mined
        dcr, la = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:role")

        # then roles, principals and roleAssignment should have some values
        # additionally, a org:role is provided, therefore principals and roles are different
        roles = pm4py.get_event_attribute_values(log,attribute="org:role")
        principals = pm4py.get_event_attribute_values(log, attribute="org:resource")
        self.assertEqual(dcr.roles, set(roles.keys()))
        self.assertEqual(dcr.principals, set(principals.keys()))
        self.assertNotEqual(len(dcr.roleAssignments), 0)
        self.assertNotEqual(dcr.roles, dcr.principals)


    def test_role_mining_with_exception(self):
        # if a person tries to mine for roles, but no roles or resources exist in the event log
        log = pm4py.read_xes(os.path.join('../input_data', 'running-example.xes'))
        # drop org:resource column
        log = log.drop(columns=['org:resource'])
        # when the miner is then performed
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        with self.assertRaises(ValueError) as context:
            apply(log, dcr_discover, post_process={'roles'})
        self.assertTrue('input log does not contain attribute identifiers for resources or roles' in str(context.exception))
        #note this was

    def test_role_mining_activity_without_role(self):
        # Given an event log
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        # and one event has no role
        new_row = (log[log['concept:name'] == "reinitiate request"])
        new_row = new_row.replace("Sara", float("nan"))
        for index, _ in new_row.iterrows():
            log.iloc[index] = new_row.loc[index]

        #when process is discovered

        dcr, la = pm4py.discover_dcr(log, process_type={'roles'},group_key='org:resource')
        #then reinititate request no longer has the orginal assigned role
        self.assertNotIn("reinitiate request", dcr.roleAssignments['Sara'])




















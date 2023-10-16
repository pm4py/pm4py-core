import os
import unittest

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply



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
        print(dcr)
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
        #when mined, with post_process roles
        dcr, la = apply(log, post_process='roles')
        #these attributes, will not be empty
        self.assertNotEqual(len(dcr.roles),0)
        self.assertNotEqual(len(dcr.principals),0)
        self.assertNotEqual(len(dcr.roleAssignment),0)


    def test_role_mining_with_no_roles_or_resources(self):
        #if a person tries to mine for roles, but no roles or resources exist in the event log
        log = pm4py.read_xes(os.path.join('../input_data', 'pdc/pdc_2019/Training Logs/pdc_2019_10.xes'))
        from pm4py.algo.discovery.dcr_discover.algorithm import apply
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        with self.assertRaises(Exception):
            apply(log, dcr_discover, post_process='roles')




















import os
import unittest

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriNet

from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules import utils


class ReadableTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.test_folder = '../../models/tests'

    def test_3_events_random(self):
        G = {
            'events': {'A', 'B', 'C'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {'A'},
                        'included': {'A', 'B', 'C'},
                        'pending': {'B'}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'three_events.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event_included(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event_incl.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event_pend_inc(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {'A'}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event_incl_pend.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event_pending(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {},
                        'pending': {'A'}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event_pending.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event_executed_inc(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event_exec_inc.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event_executed(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {'A'},
                        'included': {},
                        'pending': {}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event_exec.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {},
                        'pending': {}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event.tapn')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertEqual(len(tapn.places), p)
        self.assertEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_one_event_unoptimized(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {},
                        'pending': {}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'one_event_full.tapn')
        d2p = Dcr2PetriNet(preoptimize=False, map_unexecutable_events=True)

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_skeleton(self):
        '''
        
        '''
        G = {
            'events': {},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {},
                        'pending': {}
                        }
        }
        tapn_path = os.path.join(self.test_folder, 'test.pnml')
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def tearDown(self) -> None:
        tests_model_folder = '../../models/tests/'
        for filename in os.listdir(tests_model_folder):
            os.remove(os.path.join(tests_model_folder, filename))


if __name__ == '__main__':
    unittest.main()

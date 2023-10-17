import os
import unittest

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriNet
from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules import utils


class ReadableTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.test_folder = '../../models/tests'

    def test_relation_response_pending(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {'B'}
                        }
        }
        tapn_path = self.test_folder + '/response_pend.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_response(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/response.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_exclude_excluded(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/exclude_excluded.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_exclude(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/exclude.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_exclude_pending(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {'B'}
                        }
        }
        tapn_path = self.test_folder + '/exclude_pending.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_include_excluded_pending(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {'B'}
                        }
        }
        tapn_path = self.test_folder + '/include_excluded_pending.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_include_excluded(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/include_excluded.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_include(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/include.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_cond(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/cond.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_cond_exec(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {'B'},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/cond_exec.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_milestone(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'B'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/milestone.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_milestone_pending(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'B'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {'A'}
                        }
        }
        tapn_path = self.test_folder + '/milestone_pend.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_noresp(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A': {'B'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = self.test_folder + '/noresp.tapn'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_noresp_pending(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A': {'B'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {'B'}
                        }
        }
        tapn_path = self.test_folder + '/noresp_pend.tapn'
        d2p = Dcr2PetriNet()

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
        tapn_path = self.test_folder + '/test.pnml'
        d2p = Dcr2PetriNet()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)

    def tearDown(self) -> None:
        for filename in os.listdir(self.test_folder):
            os.remove(os.path.join(self.test_folder, filename))


if __name__ == '__main__':
    unittest.main()

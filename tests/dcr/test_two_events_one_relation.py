import unittest

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriTransport
from pm4py.objects.conversion.dcr.variants import dcr_to_pn_utils


class ReadableTestCase(unittest.TestCase):

    def test_relation_response_pending(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A':{'B'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {'B'}
                        }
        }
        tapn_path = '../models/fase/relation/response_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_response(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A':{'B'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/response.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_exclude_excluded(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A':{'B'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/exclude_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_exclude(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A':{'B'}},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/exclude.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_exclude_pending(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A':{'B'}},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {'B'}
                        }
        }
        tapn_path = '../models/fase/relation/exclude_pending.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_include_excluded_pending(self):
        G = {
            'events': {'A','B'},
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
        tapn_path = '../models/fase/relation/include_excluded_pending.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_relation_include_excluded(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A':{'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/include_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_include(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A':{'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/include.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_cond(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {'A':{'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/cond.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_cond_exec(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {'A':{'B'}},
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
        tapn_path = '../models/fase/relation/cond_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_milestone(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {'A':{'B'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/milestone.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_milestone_pending(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {'A':{'B'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {'A'}
                        }
        }
        tapn_path = '../models/fase/relation/milestone_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_noresp(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A':{'B'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/relation/noresp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

    def test_relation_noresp_pending(self):
        G = {
            'events': {'A','B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A':{'B'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {'B'}
                        }
        }
        tapn_path = '../models/fase/relation/noresp_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

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
        tapn_path = '../models/fase/test.pnml'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p,t,a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p,len(tapn.places))
        self.assertEqual(t,len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs),a)

if __name__ == '__main__':

    unittest.main()
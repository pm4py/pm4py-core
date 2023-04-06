import unittest

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriTransport
from pm4py.objects.conversion.dcr.variants import util


class ReadableTestCase(unittest.TestCase):

    def test_2c_cond_mil(self):
        '''
        TODO milestone
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
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
        tapn_path = '../models/fase/reciprocal/2c_cond_mil.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2c_cond_mil_pend(self):
        '''
        TODO milestone
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
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
        tapn_path = '../models/fase/reciprocal/2c_cond_mil_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_resp_no_resp(self):
        '''
        TODO noresp
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {'A': {'B'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_resp_no_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_incl_excl(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_incl_excl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_incl_excl_excluded(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_incl_excl_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_incl_resp(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_incl_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_incl_resp_excluded(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_incl_resp_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_excl_no_resp(self):
        '''
        TODO no-resp
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A': {'B'}},
            'includesTo': {},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_excl_no_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_excl_resp(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'B'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_excl_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2e_incl_no_resp(self):
        '''
        TODO no-resp
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'B'}},
            'noResponseTo': {},
            'includesTo': {'A': {'B'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2e_incl_no_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_ec_mil_incl(self):
        '''
        TODO: mil
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'B'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'B': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/ec_mil_incl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_ec_mil_excl(self):
        '''
        TODO milestone
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'B'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'B': {'A'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/ec_mil_excl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_ec_mil_resp(self):
        '''
        TODO milestone
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'B'}},
            'responseTo': {'B': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/ec_mil_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_ec_mil_no_resp(self):
        '''
        TODO milestone
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'B'}},
            'responseTo': {},
            'noResponseTo': {'B': {'A'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/ec_mil_no_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2ec_cond_incl(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'B': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2ec_cond_incl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2ec_cond_incl_excluded(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'B': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2ec_cond_incl_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2ec_cond_excl(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'B': {'A'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2ec_cond_excl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_2ec_cond_resp(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {'B': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/2ec_cond_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_3ec_cond_resp_incl(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {'B': {'A'}},
            'noResponseTo': {},
            'includesTo': {'B': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/3ec_cond_resp_incl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_3ec_cond_resp_excl(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {'B': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'B': {'A'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/3ec_cond_resp_excl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_4ec_cond_resp_incl_excl(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {'B': {'A'}},
            'noResponseTo': {},
            'includesTo': {'B': {'A'}},
            'excludesTo': {'B': {'A'}},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/4ec_cond_resp_incl_excl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_4ec_cond_resp_incl_excl_dumn(self):
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'B': {'A'}},
            'milestonesFor': {},
            'responseTo': {'B': {'A'}},
            'noResponseTo': {},
            'includesTo': {'B': {'A'}},
            'excludesTo': {'B': {'A'}},
            'marking': {'executed': {},
                        'included': {'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/4ec_cond_resp_incl_excl_dumn.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_ec_cond_no_resp(self):
        '''
        TODO noresp
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {'A': {'B'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'B': {'A'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A', 'B'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/reciprocal/ec_cond_no_resp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_skeleton(self):
        '''
        
        '''
        G = {
            'events': {'A', 'B'},
            'conditionsFor': {},
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
        tapn_path = '../models/fase/test.pnml'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)


if __name__ == '__main__':
    unittest.main()

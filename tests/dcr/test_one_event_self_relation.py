import unittest

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriTransport
from pm4py.objects.conversion.dcr.variants import util


class ReadableTestCase(unittest.TestCase):

    def test_self_response_pending(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {'A'}
                        }
        }
        tapn_path = '../models/fase/self/self_response_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_response(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_response.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_exclude_excluded(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {},
                        'included': {},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_exclude_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_exclude(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_exclude.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_inc_exc(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'A'}},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_inc_exc.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_include_excluded(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_include_excluded.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_include(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_include.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_response_exclude(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_resp_excl.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_response_exclude_pending(self):
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {'A'}
                        }
        }
        tapn_path = '../models/fase/self/self_resp_excl_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
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
        tapn_path = '../models/fase/self/self_cond.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
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
        tapn_path = '../models/fase/self/self_cond_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_incl_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {'A': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_cond_incl_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_excl_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_cond_excl_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_resp_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_cond_resp_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_resp_incl_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {'A': {'A'}},
            'excludesTo': {},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_cond_resp_incl_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_resp_excl_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_cond_resp_excl_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_cond_resp_incl_excl_exec(self):
        G = {
            'events': {'A'},
            'conditionsFor': {'A': {'A'}},
            'milestonesFor': {},
            'responseTo': {'A': {'A'}},
            'noResponseTo': {},
            'includesTo': {'A': {'A'}},
            'excludesTo': {'A': {'A'}},
            'marking': {'executed': {'A'},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_cond_resp_incl_excl_exec.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(2, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_milestone(self):
        '''
        TODO: First implement the milestone mapping
        Returns
        -------

        '''
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'A'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_milestone.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_milestone_pending(self):
        '''
        TODO: First implement the milestone mapping
        Returns
        -------

        '''
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {'A': {'A'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {'A'}
                        }
        }
        tapn_path = '../models/fase/self/self_milestone_pend.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_noresp(self):
        '''
        TODO: First implement the noresponse mapping
        Returns
        -------

        '''
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A': {'A'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {}
                        }
        }
        tapn_path = '../models/fase/self/self_noresp.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)

    def test_self_noresp_pending(self):
        '''
        TODO: First implement the noresponse mapping
        Returns
        -------

        '''
        G = {
            'events': {'A'},
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {'A': {'A'}},
            'includesTo': {},
            'excludesTo': {},
            'marking': {'executed': {},
                        'included': {'A'},
                        'pending': {'A'}
                        }
        }
        tapn_path = '../models/fase/self/self_noresp_pend.tapn'
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

        p, t, a = util.get_expected_places_transitions_arcs(G)
        self.assertEqual(p, len(tapn.places))
        self.assertEqual(t, len(tapn.transitions))
        self.assertLessEqual(len(tapn.arcs), a)


if __name__ == '__main__':
    unittest.main()

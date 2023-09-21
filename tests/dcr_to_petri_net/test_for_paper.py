import os
import unittest

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriTransport

from pm4py.objects.conversion.dcr.variants.to_petri_net_submodules import utils


class PnTestCase(unittest.TestCase):

    def test_paper_example(self):
        '''
        
        '''
        G = {
            'events': {'EditPaymentInfo', 'AddOrder', 'Checkout'},
            'conditionsFor': {'Checkout': {'EditPaymentInfo'}},
            'milestonesFor': {},
            'responseTo': {'AddOrder': {'Checkout'}},
            'noResponseTo': {},
            'includesTo': {'AddOrder': {'Checkout'}, 'Checkout': {'AddOrder'}},
            'excludesTo': {'Checkout': {'Checkout'}, 'AddOrder': {'AddOrder'}},
            'marking': {'executed': {},
                        'included': {'EditPaymentInfo', 'AddOrder'},
                        'pending': {}
                        }
        }
        tapn_path = '../../models/test/petrinets_paper_example.tapn'
        d2p = Dcr2PetriTransport()

        tapn, m = d2p.dcr2tapn(G, tapn_path)

        p, t, a = utils.get_expected_places_transitions_arcs(G)
        # assertions are done using less than equal because p,t,a are always theoretical upper bounds
        # due to preoptimization on the dcr graph and reachability analysis on the pn these are always less or equal
        self.assertLessEqual(len(tapn.places), p)
        self.assertLessEqual(len(tapn.transitions), t)
        self.assertLessEqual(len(tapn.arcs), a)
        os.remove(tapn_path)


if __name__ == '__main__':
    unittest.main()

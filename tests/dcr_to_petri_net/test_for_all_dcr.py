import unittest
import os
import itertools
from copy import deepcopy
from itertools import combinations

from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriTransport


def one_permutation_test(key, dcr_graph):
    file_name = key.replace("'", "").replace("(", "").replace(")", "").replace(",", "").replace(" ", "_")
    file_name = file_name + ".tapn"
    res_path = f"../models/all/{file_name}"
    d2p = Dcr2PetriTransport(postoptimize=False)
    tapn = d2p.dcr2tapn(dcr_graph, res_path)
    return tapn, res_path


def parse_permutation_to_key(relations=None, events=None, marking=None):
    if events is None:
        events = ['A', 'B']
    if marking is None:
        marking = [(1, 0, 0), (1, 0, 0)]
    key = "rel_"
    if len(events) == 1:
        key = "self_"
    frozenset_repr = repr(relations).replace(" ", "")
    key = key + frozenset_repr
    for i in [0,1]:
        e = events[i]
        m = marking[i]
        key = key + "_" + e + f"({m[0]},{m[1]},{m[2]})"
    return key


class MyTestCase(unittest.TestCase):


    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def setUp(self) -> None:
        self.dcr_template = {
            'events': set(),
            'conditionsFor': {},
            'milestonesFor': {},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'conditionsForDelays': {},
            'responseToDeadlines': {},
            'marking': {'executed': set(),
                        'included': set(),
                        'pending': set()
                        }
        }
        self.prepare_all_permutations()
        super().setUp()

    def prepare_all_permutations(self):
        self.effect_relations = ['includesTo', 'excludesTo', 'responseTo', 'noResponseTo']
        self.constrain_relations = ['conditionsFor', 'milestonesFor']
        self.all_relations = self.effect_relations + self.constrain_relations
        e1 = 'A'
        e2 = 'B'
        self.dcrs_to_test = {}
        for j in [1, 2]:
            for i in range(6, 0, -1):
                for comb in combinations(self.all_relations, i):
                    for (ai,ae,ap) in itertools.product([True, False], repeat=3):
                        dcr = deepcopy(self.dcr_template)
                        if j == 1:
                            dcr['events'].add(e1)
                            if ai:
                                dcr['marking']['included'].add(e1)
                            if ae:
                                dcr['marking']['executed'].add(e1)
                            if ap:
                                dcr['marking']['pending'].add(e1)
                            for rel in comb:
                                if not e1 in dcr[rel]:
                                    dcr[rel][e1] = set()
                                dcr[rel][e1].add(e1)
                            key = f'self_{repr(comb)}_A{1 if ai else 0}{1 if ae else 0}{1 if ap else 0}'
                            self.dcrs_to_test[key] = dcr
                        else:
                            dcr['events'].add(e1)
                            if ai:
                                dcr['marking']['included'].add(e1)
                            if ae:
                                dcr['marking']['executed'].add(e1)
                            if ap:
                                dcr['marking']['pending'].add(e1)

                            dcr['events'].add(e2)
                            for pula in itertools.product([True, False], repeat=3):
                                print(pula)
                                (bi, be, bp) = pula
                                if bi:
                                    dcr['marking']['included'].add(e2)
                                if be:
                                    dcr['marking']['executed'].add(e2)
                                if bp:
                                    dcr['marking']['pending'].add(e2)
                                for rel in comb:
                                    if rel in self.constrain_relations:
                                        if not e2 in dcr[rel]:
                                            dcr[rel][e2] = set()
                                        dcr[rel][e2].add(e1)
                                    else:
                                        if not e1 in dcr[rel]:
                                            dcr[rel][e1] = set()
                                        dcr[rel][e1].add(e2)
                                key = f'rel_{repr(comb)}_A{1 if ai else 0}{1 if ae else 0}{1 if ap else 0}_B{1 if bi else 0}{1 if be else 0}{1 if bp else 0}'
                                if key == 'rel_conditionsFor_A100_B100':
                                    print(dcr)
                                self.dcrs_to_test[key] = dcr

    def prepare_one_test(self, relations, events, marking):
        key = parse_permutation_to_key(relations, events, marking)
        tapn, res_path = one_permutation_test(key, self.dcrs_to_test[key])
        return tapn, res_path

    def test_complete(self):
        past_k = None
        i = 0
        counter = 0
        for k, v in self.dcrs_to_test.items():
            k_split = k.split('_')
            file_name = k.replace("'", "").replace("(", "").replace(")", "").replace(",", "").replace(" ", "_")
            file_name = file_name + ".tapn"
            res_path = f"../../models/tests/{file_name}"
            d2p = Dcr2PetriTransport(postoptimize=False)
            tapn = d2p.dcr2tapn(v, res_path)
            if k_split[1] != past_k:
                # print(f'[i] {k}')
                i = i + 1
                past_k = k_split[1]
            counter = counter + 1

        self.assertEqual(len(self.dcrs_to_test), (1 + 4 + 6 + 2 + 8 + 1 + 4 + 12 + 4 + 8 + 6 + 1 + 6) * (64 + 8))  # add assertion here
        self.assertEqual(counter, (1 + 4 + 6 + 2 + 8 + 1 + 4 + 12 + 4 + 8 + 6 + 1 + 6) * (64 + 8))  # add assertion here

    def test_one(self):
        dcr = {
            'events': {'A', 'B'},
            'conditionsFor': {'B':{'A'}},
            'milestonesFor': {'B':{'A'}},
            'responseTo': {},
            'noResponseTo': {},
            'includesTo': {},
            'excludesTo': {},
            'conditionsForDelays': {},
            'responseToDeadlines': {},
            'marking': {'executed': {},
                        'included': {'A','B'},
                        'pending': {'A'}
                        }
            }
        file_name = "one.tapn"
        res_path = f"../../models/tests/{file_name}"
        d2p = Dcr2PetriTransport(postoptimize=False)
        tapn = d2p.dcr2tapn(dcr, res_path)

    def tearDown(self) -> None:
        # comment this if you don't want to delete the results (the point of these tests is to inspect them in tapaal
        tests_model_folder = '../../models/tests/'
        for filename in os.listdir(tests_model_folder):
            os.remove(os.path.join(tests_model_folder, filename))

if __name__ == '__main__':
    unittest.main()

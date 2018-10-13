from pm4py.algo.other.petrigenerator.versions import simple_generator as petri_generator
from pm4py.algo.other.playout import factory as playout_factory
import unittest
import os


class PetriLogGeneratorTests(unittest.TestCase):
    def test_petri_log_generation(self):
        net, marking, final_marking = petri_generator.generate_petri()
        log = playout_factory.apply(net, marking)


if __name__ == "__main__":
    unittest.main()

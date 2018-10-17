from pm4py.algo.other.petrigenerator.versions import simple_generator as petri_generator
from pm4py.algo.other.playout import factory as playout_factory
import unittest


class PetriLogGeneratorTests(unittest.TestCase):
    def test_petri_log_generation(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        net, marking, final_marking = petri_generator.generate_petri()
        log = playout_factory.apply(net, marking)
        del log


if __name__ == "__main__":
    unittest.main()

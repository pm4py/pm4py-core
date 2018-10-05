import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.algo.other.petrigenerator.versions import simple_generator as petri_generator
from pm4py.algo.other.playout import factory as playout_factory


class PetriLogGeneratorTests(unittest.TestCase):
    def test_petri_log_generation(self):
        net, marking, final_marking = petri_generator.generate_petri()
        log = playout_factory.apply(net, marking)

if __name__ == "__main__":
    unittest.main()